"""
Modulo sufragio.
Permite almacenar e imprimir Boletas Únicas Electrónicas.
"""
from gi.repository.GObject import timeout_add, source_remove
from msa.core.documentos.boletas import Seleccion
from msa.core.exceptions import MesaIncorrecta
from msa.core.led_action.constants import PREVIOUS_LED_ACTION
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.base.decorators import presencia_on_required
from msa.modulos.constants import (E_CONSULTANDO, E_ESPERANDO, CHECK_READ_ONLY,
                                   E_EXPULSANDO_BOLETA, E_IMPRIMIENDO, E_REGISTRANDO,
                                   E_VOTANDO, MODULO_INICIO, MODULO_SUFRAGIO)
from msa.modulos.decorators import requiere_mesa_abierta
from msa.modulos.sufragio.constants import (PANTALLA_INSERCION_BOLETA,
                                            PANTALLA_MENSAJE_FINAL,
                                            TIEMPO_POST_IMPRESION,
                                            TIEMPO_VERIFICACION)
from msa.modulos.sufragio.controlador import Controlador
from msa.modulos.sufragio.rampa import Rampa
from msa.modulos.sufragio.registrador import Registrador
from msa.modulos.constants import (MODULO_CALIBRADOR)
from msa.core.logging import get_logger

logger = get_logger("MODULO_SUFRAGIO")


class Modulo(ModuloBase):

    """
        Módulo de votación.

        Espera a que se aproxime un tag, si esta vacío permite votar, sino
        muestra el contenido del tag.

        Si durante cualquier momento de la votación, se retira el tag, cancela
        la operación y vuelve a la pantalla de espera.
    """

    @requiere_mesa_abierta
    def __init__(self, nombre, activar_presencia=None):
        """
        Constructor
        """
        self.web_template = "sufragio"
        a_presencia = True
        if activar_presencia is not None:
            a_presencia = activar_presencia
        ModuloBase.__init__(self, nombre, activar_presencia=a_presencia)

        self.estado = None

        self.ret_code = MODULO_SUFRAGIO
        self._timeout_consulta = None
        self._consultando_tag = None

        self.registrador = Registrador(self._fin_registro, self, self._error)

        self.rampa = Rampa(self)
        self.get_brightness()
        # setting para saber cuándo es esta pantalla y luego pasar al calibrador
        self.ir_menu_salida = True
        
        # Inicio presencia por única vez en el módulo
        self.start_presencia()

    def set_estado(self, estado):
        """
        Setea el estado.

        Args:
            estado (str): Nuevo estado.
        """
        self.estado = estado

    def _set_controller(self):
        """
        Establece el controlador.
        """
        self.controlador = Controlador(self)

    def _calibrar_pantalla(self):
        """Llama al calibrador de la pantalla."""
        self.sesion.retornar_a_modulo = MODULO_SUFRAGIO
        self.ret_code = MODULO_CALIBRADOR
        self.ventana.remove(self.browser)
        self.quit()

    def _comenzar(self):
        """
        Inicializo la selección.

        Se verifica el estado. Si es distinto a "Votando" se borra el timeout
        de revisión de voto por las dudas de que alguien inserte la boleta en
        blanco inmediatamente después de revisar el voto, para evitar que la expulse.
        Esto el día de la Elección no tiene mucho sentido, pero para la capacitación sí.

        Luego se carga la pantalla ``cargar_pantalla_inicial``
        """
        self.logger.info('Intentando comenzar')
        if self.estado != E_VOTANDO and self.estado != E_IMPRIMIENDO and self.estado != E_REGISTRANDO:
            # Borramos el timeout de revisión de voto por las dudas de que
            # alguien inserte la boleta en blanco inmediatamente después de
            # revisar el voto, para evitar que la expulse. Esto el día de la
            # elección no tiene mucho sentido, pero para la capacitación sí.
            if self._timeout_consulta is not None:
                source_remove(self._timeout_consulta)
                self._timeout_consulta = None

            self.rampa.set_led_action('boleta_en_rampa')
            self.set_estado(E_VOTANDO)
            # Inicializamos una seleccion vacía para esta mesa.
            self.seleccion = Seleccion(self.sesion.mesa)
            # carga la pantalla inicial de votación. La UI sabe decidir qué
            # pantalla es
            self.controlador.send_command("cargar_pantalla_inicial")
        else:
            self.logger.warning('No se pudo comenzar porque el estado del modulo es '+self.estado)

    def set_pantalla(self, pantalla, image_data=None):
        """
        Establece la pantalla deseada.

        .. todo:: esto deberíamos deprecarlo, es overkill y tiene que ver con la
                arquitectura que usaba todo con GTK

        Args:
            pantalla (str): Representa la pantalla que se desea mostrar.
            image_data (?): Imagen que acompaña a la pantalla.
        """
        self.controlador.set_screen(pantalla, image_data=image_data)

    def expulsar_boleta(self, motivo="sufragio"):
        """
        Expulsa la boleta.
        El estado del módulo se pasa a ``EXPULSANDO_BOLETA``

        Args:
            motivo (str): Indica la razón por la cual la boleta debe
                expulsarse.
        """
        self.rampa.tiene_papel = False
        self.set_estado(E_EXPULSANDO_BOLETA)
        self.rampa.expulsar_boleta(motivo)

    def salir(self, ret_code=MODULO_INICIO):
        """
        Sale del módulo y carga el siguiente.

        Args:
            ret_code (str): El modulo al cual queremos salir.
        """
        self.salir_a_modulo(ret_code)

    def _fin_registro(self):
        """
        Se llama cuando se termina de registrar un voto.
        El estado del módulo se cambia a ``ESPERANDO``.
        """
        self.logger.info("Se muestra la pantalla de mensaje final")
        self.estado = E_ESPERANDO
        self.rampa.set_led_action('espera_en_antena')
        self.set_pantalla(PANTALLA_MENSAJE_FINAL)
        self.rampa.tiene_papel = False

        def _retornar():
            """
            Retorna a la pantalla de insercion de voto.
            """
            self.logger.info("Se llamó a la funcion retornar")
            if self.estado not in (E_CONSULTANDO, E_VOTANDO, E_REGISTRANDO):
                self.pantalla_insercion()

        # Se muestra el mensaje de agradecimiento durante 6 segundos
        timeout_add(TIEMPO_POST_IMPRESION, _retornar)

    def _guardar_voto(self):
        """
        Guarda el voto.

        Si la rampa tiene papel, se cambia al estado ``REGISTRANDO`` y,
        se procede a grabar en el chip e imprimir en el papel.

        Si la rampa no tiene papel, nos redirige a la pantalla de
        inserción de papel.
        """
        if self.rampa.tiene_papel:
            # Cambiamos el estado a "registrando"
            self.set_estado(E_REGISTRANDO)
            # Efectivamente registramos (grabamos el chip e imprimimos el papel)
            self.registrador.registrar_voto()
            # Borramos explicitamente los datos del tag.
            self.rampa.datos_tag = None
        else:
            self.pantalla_insercion()
    
    def pantalla_insercion(self, cambiar_estado=True):
        """
        Muestra la pantalla de inserción de la boleta.

        Args:
            cambiar_estado (bool): Determina si es necesarop
                cambiar el estado del módulo.
        """

        self.logger.info("Llamando a pantalla de insercion")
        
        self.seleccion = None

        # Llamo a resetear el estado de presencia en True, 
        # para reiniciar la espera de 20 segundos.
        self.controlador.presence_reset(True)
        
        if cambiar_estado:
            self.set_estado(E_ESPERANDO)
        self.rampa.set_led_action('pantalla_espera_sufragio')
        
        self.set_pantalla(PANTALLA_INSERCION_BOLETA)

    def hay_tag_vacio(self):
        """
        Arrancamos con la sesión de votación.
        """
        self._comenzar()

    def _mostrar_consulta(self, tag):
        """
        Muestra la consulta de la boleta en pantalla.
        Lo primero que se hace es traer la selección por que si esta
        apoyando un voto de una mesa de otro juego de datos lanza una
        excepción de tipo MesaIncorrecta.

        Luego se muestra la pantalla de consulta vacía.

        Se guarda el tag que estamos consultando para poder manejar el cambio
        de tag o la continuidad de la consulta de mejor manera.

        Se muestran los candidatos de la boleta en pantalla.

        Args:
            tag (SoporteDigital): Un objeto de tipo SoporteDigital.
        """
        # lo primero que hacemos es traer la seleccion por que si estamos
        # apoyando un voto de una mesa de otro juego de datos raisea una
        # excepcion de tipo MesaIncorrecta
        seleccion = Seleccion.desde_tag(tag.datos, self.sesion.mesa)

        # mostramos la pantalla vacía de consulta.
        self.controlador.consulta()
        self.rampa.set_led_action('espera_en_antena', PREVIOUS_LED_ACTION)
        self.set_estado(E_CONSULTANDO)
        # Guardamos el tag que estamos consultando para poder manejar el cambio
        # de tag o la continuidad de la consulta de mejor manera.
        self._consultando_tag = tag
        # Mostramos los candidatos de la boleta en pantalla.
        self.controlador.candidatos_consulta(seleccion)

    @presencia_on_required
    def _cambio_presencia(self, data):
        if self.estado not in (E_CONSULTANDO, E_REGISTRANDO, E_VOTANDO):
            super()._cambio_presencia(data)
        else:
            # Mientras el estado del modulo sea de consulta del voto, 
            # votando o registrando, presencia va a ser siempre True
            super()._cambio_presencia({'byte': True})

    def _consultar(self, tag):
        """
        Permite al elector consultar una boleta.

        Se evalúa el tag. En caso de que sean diferentes se muestra
        la pantalla de consulta. Si son iguales, se reduce el tiempo
        de verificación.

        Args:
            tag (SoporteDigital): Un objeto de clase SoporteDigital.
        """
        # Borramos el timeout de consulta por las dudas
        if self._timeout_consulta is not None:
            source_remove(self._timeout_consulta)
            self._timeout_consulta = None

        try:
            self.logger.warning(tag)
            # En caso de que el tag sea distinto del consultado mostramos la
            # consulta. No refrescamos si es el mismo para que no "titile" la
            # pantalla, que quedaba feo en voto <= 3.6
            if not CHECK_READ_ONLY:

                if tag != self._consultando_tag:
                    self._mostrar_consulta(tag)
                    tiempo_verificacion = TIEMPO_VERIFICACION
                else:
                    # si el tag es el mismo quiere decir que estan verificando mas
                    # tiempo, pero como no queremos que quede mucho tiempo en
                    # pantalla seteamos el timeout en 1/3 del tiempo original
                    tiempo_verificacion = TIEMPO_VERIFICACION / 3
            else:

                # La idea es que si el chip no es read_only (es decir, si no
                # tiene todos los bloques quemados), no debería mostrar la 
                # verificación del voto.
                if tag != self._consultando_tag:
                    t = tag.a_dict()
                    self.logger.warning(t)
                    if t['read_only'] is True:
                        self.logger.warning('READ ONLY = TRUE')
                        self._mostrar_consulta(tag)
                        tiempo_verificacion = TIEMPO_VERIFICACION
                    else:
                        self.logger.warning('READ ONLY = FALSE')
                        tiempo_verificacion = 0
                else:
                    # si el tag es el mismo quiere decir que estan verificando mas
                    # tiempo, pero como no queremos que quede mucho tiempo en
                    # pantalla seteamos el timeout en 1/3 del tiempo original
                    tiempo_verificacion = TIEMPO_VERIFICACION / 3

            self._timeout_consulta = timeout_add(tiempo_verificacion,
                                                 self._fin_consulta)
        except MesaIncorrecta:
            self.rampa.set_led_action('lectura_error', next_action=PREVIOUS_LED_ACTION)
            self.logger.error("El tag corresponde a una mesa de otro juego.")
            self.expulsar_boleta("juego_datos")
            self._fin_consulta()
        except Exception as err:
            self.rampa.set_led_action('lectura_error', next_action=PREVIOUS_LED_ACTION)
            self.expulsar_boleta("excepcion")
            self.logger.exception("ocurrió un error al parsear el tag.")
            self._fin_consulta()

    def _fin_consulta(self):
        """
        Fin de la rutina de consulta de boleta.

        Si en vez de apoyar la boleta metieron la boleta en la rampa la
        expulsamos.

        Returns:
            bool: No es utilizado en ningún caso hasta el momento.
        """

        # borramos la referencia al timeout
        self._timeout_consulta = None
        self.logger.debug("fin consulta!")
        # si en vez de apoyar la boleta metieron la boleta en la rampa la
        # expulsamos
        if self.rampa.tiene_papel:
            self._consultando_tag = None
            # chequeo de sanidad por si no se respetan los tiempos normales:
            if self.estado not in (E_VOTANDO, E_REGISTRANDO):
                self.expulsar_boleta("fin_consulta")
        else:
            # vuelvo a leer explicitamente el tag por que puede nunca llegar el
            # evento de inventario vacio y nos tenemos que asegurar de que si
            # no hay tag desaparezca el mensaje.
            self.rampa.tag_leido = self.rampa.get_tag()
            if self.rampa.tag_leido is None:
                # si no hay mas tag apoyado salimos
                self._consultando_tag = None
                self.pantalla_insercion()
            else:
                # Si todavia estan verificando vamos a consultar de nuevo
                self._consultar(self._consultando_tag)

        return False

    def document_ready(self):
        """
        Inicializamos cuando el browser tira el evento de document ready.

        Se levantan todas las constantes necesarias y luego,
        se llama a la rampa para que determine los pasos a
        seguir.
        """

        # Mandamos las constantes que el modulo necesita para operar.
        self.controlador.send_constants()
        # llamamos al maestro de ceremonias de la rampa para que evalúe como
        # proceder
        self.rampa.maestro()

    def menu_salida(self):
        """
        Muestra el menú que nos permite salir o abrir asistida.
        """
        self.es_menu_salida = True
        self.controlador.menu_salida()

    def hide_dialogo(self):
        """
        Oculta el diálogo.
        """
        self.controlador.hide_dialogo()

    def _error(self, cambiar_estado=True):
        """ Función de error, si el guardado de la boleta fue erróneo,
            se muestra un mensaje acorde.
        """
        self.rampa.set_led_action('error_impresion')
        self.logger.debug("Error tag no guardado o no impreso")
        # Hacemos un ruido para que el elector preste atención y que las
        # autoridades esten al tanto de un posible problema al emitir la boleta
        self.play_sonido_error()
        self.rampa.tiene_papel = False
        # Mostramos la pantalla de insercion para ocultar la selección de
        # candidatos que hizo el elector y así evitar que cualquier otra
        # persona pueda verlo
        self.pantalla_insercion(cambiar_estado)

        def aceptar_error():
            # Primero mando a imprimir el template de error
            #tag = self.rampa.tag_leido
            #self.rampa.imprimir_serializado("Invalida", tag=self.rampa.get_tag())
            pass    
        # Mostramos el popup de error el la UI
        self.controlador.cargar_dialogo("msg_error_grabar_boleta",
                                        aceptar=aceptar_error)
