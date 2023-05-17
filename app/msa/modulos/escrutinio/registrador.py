"""Registrador del modulo escrutinio.

Orquesta el orden y maneja la impresion de actas y certificados.
"""
from base64 import b64encode
from ujson import dumps

from gi.repository.GObject import timeout_add
from msa.core.data.candidaturas import Categoria
from msa.core.documentos.constants import (CIERRE_CERTIFICADO,
                                           CIERRE_COPIA_FIEL,
                                           CIERRE_ESCRUTINIO, CIERRE_RECUENTO,
                                           CIERRE_TRANSMISION)
from msa.modulos import get_sesion
from msa.settings import QUEMA


class RegistradorCierre(object):

    """Registrador para la Apertura."""

    def __init__(self, secuencia):
        """Constructor del registrador del cierre."""

        self.sesion = get_sesion()

        self._reiniciar_reintentos()

        self.secuencia = secuencia

    def _reiniciar_reintentos(self):
        self.reintentos_grabacion = 0

    def _guardar_tag(self, tag, categoria=None):
        """ Guarda los datos en el tag, lo vuelve a leer y compara los dos
            strings para verificar la correcta escritura.
            Devuelve True si el guardado y la comprobación están correctos,
            False en caso contrario.
        """
        # serializar, recalculando el código de control:
        
        self.sesion.recuento.invalidar_control()
        aes_key = self.sesion.mesa.get_aes_key()
        datos = self.sesion.recuento.a_tag(categoria,
                               cant_dni_max=len(self.sesion.recuento.autoridades),
                               aes_key=aes_key, serial=tag.serial)
        
        self.secuencia.rampa.guardar_tag_async(self.tag_guardado, 
                                               self.sesion.recuento.tipo_tag, 
                                               datos, 
                                               QUEMA)
        return True

    def tag_guardado(self, resultado):
        if resultado:
            self._imprimir_acta()
        elif not resultado and self.reintentos_grabacion > 0:
            self.secuencia.rampa.reset_rfid()
            self.reintentos_grabacion -= 1
        else:
            self.secuencia._error_impresion()

    def registrar_acta(self):
        """ Función que se encarga primero de guardar los datos y corroborar
        que esté todo ok. Si es así imprime y devuelve True o False en
        cualquier caso contrario
        """
        tag = self.secuencia.rampa.get_tag()
        tipo_acta = self.secuencia.acta_actual

        if (self.secuencia.es_acta_actual_con_chip() and
                tag is not None and tag.vacio):
            # Si el acta tiene chip se guarda en el mismo y se imprime
            self._registrar_acta_con_chip(tag, tipo_acta)
        elif (self.secuencia.es_acta_actual_sin_chip() and
                tag is None):
            # Si no tiene chip solo se imprime
            self._registrar_acta_sin_chip()
        else:
            self.secuencia._error_impresion()

    def _registrar_acta_con_chip(self, tag, tipo_acta):
        """Registra el acta en caso de ser 'con chip' (no es un certificado)."""
        _, cod_categoria = tipo_acta
        # Tiene que si o si tener tag.
        self._guardar_tag(tag, cod_categoria)

    def _registrar_acta_sin_chip(self):
        """Registra los certificados."""
        # si tiene tag no imprime.
        self._imprimir_acta()

    def _get_extra_data(self, tipo_acta, serializar_dni=True):
        """
        Genera la data extra para mandarle al servicio de impresión.

        Args:
            tipo_acta (str): Indica el tipo de acta.
            serializar_dni (bool): Configuración para decidir la impresión
                del DNI.

        Returns:
            dict: Diccionario con información extra. Se agrega autoridades
            de mesa.
        """
        recuento = self.sesion.recuento
        extra_data = recuento.get_extra_data(tipo_acta, serializar_dni)
        
        return dumps(extra_data)

    def _imprimir_acta(self, serializar_dni=True):
        """Imprime las actas."""
        def _imprimir():
            tipo_acta = self.secuencia.acta_actual

            tag = self.sesion.recuento.a_tag(tipo_acta[1],
                                             con_dnis=serializar_dni)
            encoded_data = b64encode(tag)
            extra_data = self._get_extra_data(tipo_acta, serializar_dni)
            self.secuencia.rampa.imprimir_serializado("Recuento", encoded_data,
                                            extra_data=extra_data)
        timeout_add(100, _imprimir)


class SecuenciaActas(object):

    """Clase que maneja la secuencia de impresión de actas."""

    _imprimiendo = False

    def __init__(self, actas_con_chip, actas_sin_chip, modulo, callback_espera, callback_error_registro,
                 callback_imprimiendo, callback_fin_secuencia,
                 callback_post_fin_secuencia=None, impresion_extra=True):
        """Constructor la clase de la secuencia de impresion de actas."""

        self._actas_con_chip = actas_con_chip
        self._actas_sin_chip = actas_sin_chip

        self.modulo = modulo
        # Se llama cuando se esta esperando el ingreso de papel.
        self.callback_espera = callback_espera
        # Se llama cuando hay un error de registro.
        self.callback_error_registro = callback_error_registro
        # Se llama cuando se está por imprimir
        self.callback_imprimiendo = callback_imprimiendo
        # se llama cuando termina la secuencia de impresion de actas
        self.callback_fin_secuencia = callback_fin_secuencia
        self.callback_post_fin_secuencia = callback_post_fin_secuencia

        # Cuando finaliza la secuencia de actas, se permite a los fiscales
        # imprimir actas extra. 
        self.impresion_extra = impresion_extra

        self.orden_actas = self.modulo.orden_actas

        self.logger = modulo.sesion.logger
        self.sesion = modulo.sesion
        self.actas_a_imprimir = self._crear_lista_actas()
        self.rampa = self.modulo.rampa
        self.registrador = RegistradorCierre(secuencia=self)
        self.acta_actual = None
        self._finalizado = False
        self._check_eimpresion_ms = 50
        self._impresion_checks = None
        self._impresion_ms = 20000
        self.logger.info("Creado objeto de secuencia de actas")

    def es_acta_actual_con_chip(self) -> bool:
        return self.acta_actual[0] in self._actas_con_chip

    def es_acta_actual_sin_chip(self) -> bool:
        return self.acta_actual[0] in self._actas_sin_chip

    def _crear_lista_actas(self):
        """
        Crea la lista de la secuencia de impresión de actas.

        Returns:
            array.array: Arreglo con las actas ordenadas por la secuencia especificada
            en la constante ``SECUENCIA_CERTIFICADOS``
        """
        actas = []
        categorias = Categoria.many(sorted="posicion")
        grupos = sorted(list(set([cat.id_grupo for cat in categorias])))

        for tipo_acta in self.orden_actas:
            for grupo in grupos:
                datos_grupo = [tipo_acta, grupo]
                actas.append(datos_grupo)
        self.logger.info("Creanda lista de actas. %s actas a imprimir",
                         len(actas))
        return actas

    @staticmethod
    def _crear_lista_cierre_certificado():
        actas = []
        categorias = Categoria.many(sorted="posicion")
        grupos = sorted(list(set([cat.id_grupo for cat in categorias])))
        
        for grupo in grupos:
            datos_grupo = [CIERRE_ESCRUTINIO, grupo]
            actas.append(datos_grupo)
        return actas


    def get_cat_preferencia_actual(self):
        return self.__cat_pref_actual

    def _determinar_acta_actual(self):
        self.acta_actual = self.actas_a_imprimir.pop(0)
        self.actas_por_mesa_total = self.get_total_actas()
        categorias_disponibles = Categoria.many(sorted="posicion")

        # Averiguamos si en el grupo hay cargos con preferencias
        grupo_cats = Categoria.many(sorted="posicion", id_grupo=self.acta_actual[1], max_preferencias__gte=1)
        self._imprimiendo_preferencias = len(grupo_cats) > 0
        self.logger.info('Imprimiendo preferencias {}'.format(self._imprimiendo_preferencias))
        self.__cat_pref_actual = Categoria.first(sorted="posicion",  id_grupo=self.acta_actual[1]).codigo
        self.logger.info("Categoria actual: "+self.__cat_pref_actual)
        self.acta_por_mesa_actual = None
        for index in range(len(categorias_disponibles)):
            if categorias_disponibles[index].codigo == self.__cat_pref_actual:
                self.acta_por_mesa_actual = index+1
        self.logger.info("Acta actual: "+str(self.acta_por_mesa_actual))

    def ejecutar(self):
        """Ejecuta la secuencia de impresión de actas."""
        self.logger.info("Ejecutando secuencia de impresion")
        try:
            if len(self.actas_a_imprimir) > 0:
                self.rampa.remover_boleta_expulsada()
                self._determinar_acta_actual()
                self._pedir_acta()
            else:
                if self.impresion_extra:
                    # cuando terminamos de imprimir todas las actas cambiamos los
                    # callbacks para la impresion extra de actas para fiscales.
                    self._finalizado = True
                    self.rampa.set_led_action('reset')
                    self.actas_a_imprimir = SecuenciaActas._crear_lista_cierre_certificado()
                    self._determinar_acta_actual()
            
                if self.callback_fin_secuencia is not None:
                    self.callback_fin_secuencia()
                    self.callback_fin_secuencia = self.callback_post_fin_secuencia

        except IndexError as e:
            self.logger.exception(e)
            if self.callback_fin_secuencia is not None:
                self.callback_fin_secuencia()
                self.callback_fin_secuencia = self.callback_post_fin_secuencia
        except Exception as e:
            self.logger.exception(e)
                        
    def _pedir_acta(self):
        """Pedimos el ingreso del acta."""
        self.logger.info("Pidiendo acta: %s", self.acta_actual[0])
        self.rampa.set_led_action('solicitud_acta')
        self.callback_espera(self.acta_actual)
        self.rampa.remover_insertando_papel()
        self.rampa.remover_consultar_tarjeta()
        self.rampa.registrar_nuevo_papel(self._imprimir_acta)

    def _fin_impresion(self, *args):
        """Se llama cuando termina de imprimir."""
        self.logger.info("Fin de la impresion")
        self._imprimiendo = False
        self.registrador._reiniciar_reintentos()
        self.ejecutar()

    def _imprimir_acta(self, data_sensores):
        """Manda a imprimir el acta."""
        if not self._imprimiendo:
            self._imprimiendo = True
            self.rampa.remover_insertando_papel()
            self.rampa.remover_consultar_tarjeta()

            self.logger.info("Imprimiendo acta")
            if self.callback_imprimiendo is not None:
                self.logger.info("callback_imprimiendo")
                self.callback_imprimiendo(self.acta_actual, self._finalizado)
            # tiramos este timeout porque sino no actualiza el panel de estado
            timeout_add(200, self._impresion_real)
        else:
            self.logger.warning("Frenado intento de impresion concurrente")
            self.logger.warning("self._impresion_checks: "+str(self._impresion_checks))
            if self._impresion_checks is None:
                self._impresion_checks = 0
                timeout_add(self._check_eimpresion_ms, self._revisar_estado_impresion)

    def _revisar_estado_impresion(self):
        if self._imprimiendo:
            self._impresion_checks += 1
            if self._impresion_checks > int(self._impresion_ms / self._check_eimpresion_ms):
                self.logger.warning("Lanzando error de impresión internamente")
                self._error_impresion()
                self._impresion_checks = None
                return False
            else:
                self.logger.warning("Cantidad de checks impresion: "+str(self._impresion_checks))
                return True
        else:
            self.logger.warning("Check impresión finalizado, imprimiendo es false")
            self._impresion_checks = None
            return False



    def _impresion_real(self):
        """Efectivamente manda a imprimir el acta."""
        self.logger.info("Por registrar acta")
        #self.rampa.set_led_action('impresion')
        self.rampa.registrar_error_impresion(self._error_impresion)
        try:
            self.rampa.registrar_boleta_expulsada(self._fin_impresion)
            self.registrador.registrar_acta()
        except ValueError as e:
            # la cantidad de votos excede lo que smart_numpacker puede guardar
            self.logger.exception(e)

    def _error_impresion(self):
        """
        Ante el evento de error de impresión, se procede a ejecutar
        los pasos necesarios establecido por el protocolo. Es decir, se remueve
        la boleta, se informa el error junto con la boleta en cuestión, el estado de
        impresión queda en falso y se procede a reintentar la operación.

        Existe un logger que aporta una breve descripción.
        """
        self.rampa.set_led_action('error_impresion', 'solicitud_acta')
        self.logger.info("Acta NO registrada")
        self.rampa.remover_boleta_expulsada()
        self.callback_error_registro(self.acta_actual, self._finalizado)
        self._imprimiendo = False
        self.registrador._reiniciar_reintentos()

    def get_total_actas(self):
        cantidad = len(Categoria.many(sorted="posicion"))
        self.logger.info("Total Actas -> Cantidad %s ", cantidad)
        return cantidad
