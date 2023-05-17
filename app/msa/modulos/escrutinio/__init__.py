"""Modulo para hacer Escrutinio y Cierre de Mesa."""
from datetime import datetime

from msa.core.audio.settings import VOLUMEN_ESCRUTINIO_P2, VOLUMEN_GENERAL
from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.core.documentos.actas import Recuento
from msa.core.documentos.boletas import Seleccion
from msa.core.led_action.constants import PREVIOUS_LED_ACTION
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.constants import (E_IMPRIMIENDO, E_RECUENTO, MODULO_INICIO,
                                   MODULO_RECUENTO, SHUTDOWN)
from msa.modulos.decorators import requiere_mesa_abierta
from msa.modulos.escrutinio.constants import (ACT_BOLETA_NUEVA,
                                              ACT_BOLETA_REPETIDA, ACT_ERROR,
                                              ACT_VERIFICAR_ACTA,
                                              SECUENCIA_CERTIFICADOS, TIPO_ACTAS, PRINTER_QUALITY_MAP)
import importlib
from msa.modulos.escrutinio.rampa import Rampa
from msa.modulos.escrutinio.registrador import SecuenciaActas


class Modulo(ModuloBase):
    """
    Modulo de Recuento de votos.

    Este módulo permite hacer el recuento de votos de una mesa.
    El usuario debe pasar el tag a ser utilizado para el recuento de la
    mesa, y a continuación debe pasar todas las boletas por el lector.
    El sistema va a totalizarlas y una vez que el usuario confirme el
    cierre de la mesa, emite un listado con la cantidad de copias
    indicadas.
    """

    @requiere_mesa_abierta
    def __init__(self, nombre, activar_presencia=None):
        """Constructor"""
        self.web_template = "escrutinio"
        
        a_presencia = True
        if activar_presencia is not None:
            a_presencia = activar_presencia
        ModuloBase.__init__(self, nombre, activar_presencia=a_presencia)
        self._start_audio()
        self.apertura = self.sesion.apertura
        self.ret_code = MODULO_RECUENTO
        self.get_rampa()
        self.set_volume()
        if self.sesion.recuento is None:
            self.sesion.recuento = Recuento(self.sesion.mesa)
        self.estado = E_RECUENTO
    
        self.config_files = [COMMON_SETTINGS, nombre, "imaging"]
        self._load_config()
        self.get_orden_certs()

        self._ultimo_tag_leido = None
        self._hora_ultimo_tag = self._hora_inicio = datetime.now()
        self.get_brightness()
        self.start_presencia()  # ModuloBase

        if self.config('cambiar_calidad_impresion'):
            
            self._original_print_quality = self.rampa._servicio.get_printer_quality()[0]['byte']
            
            for value in PRINTER_QUALITY_MAP.values():
                if self._original_print_quality < value:
                    self._original_print_quality = value
                    break
 
            self.rampa._servicio.set_printer_quality(PRINTER_QUALITY_MAP[self.config('calidad_impresion')])
           
        self.rampa.set_led_action('pantalla_espera_sufragio')


    def set_volume(self):
        """
        Se establece el volumen para reproducir los sonidos de la
        máquina. Utilizado espcielamente en modo de asistida.

        Dicho volumen depende de las constantes ``VOLUMEN_GENERAL`` o
        ``VOLUMEN_ESCRUTINIO_P2``.

        """
        volumen = VOLUMEN_GENERAL
        if self.rampa.tiene_conexion:
            version = self.rampa.get_arm_version()
            if version == 1:
                volumen = VOLUMEN_ESCRUTINIO_P2
        self._player.set_volume(volumen)

    def get_orden_certs(self):
        """
        Se establece el orden en que los certificados se deben procesar.
        El mismo se establece por medio de la constante ``SECUENCIA_CERTIFICADOS``.
        """
        secuencia_actas = self.config("secuencia_actas")
        self.orden_actas = SECUENCIA_CERTIFICADOS[secuencia_actas]

    def _set_controller(self):
        """
        Se crea una instancia del Controlador.
        """
        
        nombre_controlador_escrutino = self.config("controlador")
        Controlador = getattr(importlib.import_module("msa.modulos.escrutinio.controlador"), nombre_controlador_escrutino)
        
        self.controlador = Controlador(self)

    def get_rampa(self):
        """
        Se crea una instancia de la Rampa.
        """
        self.rampa = Rampa(self)

    def _inicio(self):
        """ Función llamada desde el controlador una vez que se encuentra lista
            la interfaz web.
        """
        pass

    def beep(self, tipo_actualizacion):
        """
        En base a la actualización recibida, se procede a emitir un sonido
        que indica el estado de error, warning u ok de la máquina.

        Args:
            tipo_actualizacion (str): Indica el nuevo estado de las actas.
        """
        if tipo_actualizacion == ACT_BOLETA_NUEVA:
            self.play_sonido_ok()
        elif tipo_actualizacion == ACT_BOLETA_REPETIDA:
            self.play_sonido_warning()
        elif tipo_actualizacion == ACT_ERROR:
            self.play_sonido_error()

    def procesar_voto(self, tag):
        """
        Procesa un voto que se apoya. Actúa en consecuencia.
        En caso de que estado sea ``RECUENTO``, se obtiene del tag
        la mesa y los datos asociados para sumar los votos. También se
        recupera el serial del tag y calcula cuanto tiempo transcurrió
        desde la última vez que la boleta fue leída (para suplir factores
        humanos).
        Luego actualiza el estado de la máquina.

        Args:
            tag (str): Un objeto SoporteDigital
        """
        tipo_actualizacion = ACT_ERROR
        seleccion = None
        if self.estado == E_RECUENTO:
            try:
                # usamos el serial como unicidad, esto podría cambiar
                unicidad = tag.serial
                # Parseamos la seleccion
                seleccion = Seleccion.desde_tag(tag.datos, self.sesion.mesa)
                # A veces puede llegar mas de un evento de tag nuevo al mismo
                # tiempo, como es un factor humano dificil de manejar lo que
                # hacemos es no tirar dos eventos seguidos del mismo tag por
                # que las autoridades de mesa "se asustan" si ven un "boleta
                # repetida" inmediatamente despues de que apoyaron el tag de
                # una boleta nueva. Para evitar confusiones no procesamos la
                # boleta que se acaba de procesar y la pantalla no se refresca
                # si la ultima lectura de la misma boleta fue hace menos de un
                # segundo.
                delta = datetime.now() - self._hora_ultimo_tag
                if tag.serial != self._ultimo_tag_leido or delta.seconds > 0:
                    # Si el voto no fue ya contado se suma.
                    if not self.sesion.recuento.serial_sumado(unicidad):
                        self._sumar_voto(seleccion, unicidad)
                        self.rampa.set_led_action('lectura_ok', PREVIOUS_LED_ACTION)
                        tipo_actualizacion = ACT_BOLETA_NUEVA
                    else:
                        # En caso de estar ya somado se avisa y no se cuenta.
                        self.rampa.set_led_action('lectura_repetida', PREVIOUS_LED_ACTION)
                        tipo_actualizacion = ACT_BOLETA_REPETIDA
                else:
                    tipo_actualizacion = None
            except Exception as e:
                # cualquier circunstancia extraña se translada en un error.
                self.rampa.set_led_action('lectura_error', PREVIOUS_LED_ACTION)
                self.logger.exception(e)
                seleccion = None

            if tipo_actualizacion is not None:
                self._ultimo_tag_leido = unicidad
                self._hora_ultimo_tag = datetime.now()
                self.controlador.actualizar(tipo_actualizacion, seleccion)

    def _sumar_voto(self, seleccion, unicidad):
        """
        Suma un voto al recuento.

        Args:
            seleccion (dict): Selección de candidatos realizado por el votante.
            unicidad (str): Identificador de la boleta.
        """
        # Suma la seleccion al recuento.
        self.sesion.recuento.sumar_seleccion(seleccion, unicidad)

    def preguntar_salida(self):
        """
        Llamada de la funcionalidad del controlaor para
        enviar el comando  ``preguntar_salida``.
        """
        self.controlador.preguntar_salida()

    def error_lectura(self, encender_led=True):
        """
        Llamada a la función del controlador que actualiza
        el estado de la máquina para informar un error.
        """
        if encender_led:
            self.rampa.set_led_action('lectura_error', PREVIOUS_LED_ACTION)
        self.controlador.actualizar(ACT_ERROR)

    def imprimir_documentos(self):
        """
        Realiza las últimas operaciones sobre el recuento antes de comenzar
        la impresión.
        Setea el estado de la máquina como ``IMPRIMIENDO``
        """
        self.estado = E_IMPRIMIENDO
        delta = datetime.now() - self._hora_inicio
        if self.sesion.recuento.hora:
            self.sesion.recuento.hora['segundos'] = delta.seconds
        self._iniciar_secuencia()
        self.secuencia.ejecutar()

    def habilitar_copia_certificados(self, acta_a_imprimir):
        def _fin():
            """Limpia el panel de estado cuando dejó de imprimir."""
            self.controlador.mostrar_pantalla_copias()

        self.estado = E_IMPRIMIENDO
        self._iniciar_secuencia(impresion_extra=False)
        self.secuencia.callback_fin_secuencia = _fin
        self.secuencia.callback_post_fin_secuencia = _fin
        self.secuencia.actas_a_imprimir = [(acta_a_imprimir, self.sesion.recuento.grupo_cat)]
        self.secuencia.ejecutar()

    def _iniciar_secuencia(self, impresion_extra=True):
        """Inicia la secuencia de impresion de las actas."""
        def callback_imprimiendo(tipo_acta, final=False):
            """Se llama a este callback cuando se empieza a imprimir."""
            self.controlador.hide_dialogo()
            self.rampa.set_led_action('impresion')
            self.controlador.mostrar_imprimiendo()

        def callback_espera(tipo_acta):
            """Callback que se llama para setear la pantalla de espera de
            insercion de actas."""
            self.rampa.set_led_action('solicitud_acta')
            self.controlador.pedir_acta(tipo_acta[0])

        def callback_error_registro(tipo_acta, final=False):
            """El callback al cual se llama cuando se genera un error de
            registro del acta."""
            self.rampa.expulsar_boleta()
            self.controlador.cargar_dialogo(
                "mensaje_popup_{}".format(tipo_acta[0]))

        def callback_post_fin_secuencia():
            self.controlador.set_pantalla_anterior_asistente()

        def callback_fin_secuencia():
            """Se llama cuando se terminó toda la secuencia de impresión."""
            if self.config("mostrar_asistente_cierre"):
                self.controlador.set_pantalla_asistente_cierre()
            else:
                self.controlador.mostrar_pantalla_copias()

        secuencia_actas = self.config("secuencia_actas")
        self.secuencia = SecuenciaActas(TIPO_ACTAS['con_chip'][secuencia_actas],
                                        TIPO_ACTAS['sin_chip'][secuencia_actas],
                                        self, 
                                        callback_espera,
                                        callback_error_registro,
                                        callback_imprimiendo,
                                        callback_fin_secuencia,
                                        callback_post_fin_secuencia,
                                        impresion_extra)

    def salir(self):
        """
        Le solicita al controlador salir del móodulo inicio.
        """
        self.sesion.recuento = None
        self.rampa.remover_presence_changed()

        if self.config('cambiar_calidad_impresion'):

            self.rampa._servicio.set_printer_quality(self._original_print_quality)

        self.salir_a_modulo(MODULO_INICIO)

    def apagar(self):
        """
        Le solicita al controlador salir del módulo shutdown
        (apagar la máquina).-
        """
        self.salir_a_modulo(SHUTDOWN)
