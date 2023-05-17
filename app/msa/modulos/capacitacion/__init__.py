"""
Modulo para capacitación de electores.

Muestra un menú para elegir la Ubicacion (en caso de ser más de una) y permite
elegir entre capacitar sufragio, asistida e imprimir votos en blanco para
capacitar sobre la verificacion del voto en caso de que esté activado.
"""
from gi.repository.GObject import idle_add, timeout_add
from time import sleep

from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.core.data import Ubicacion
from msa.core.documentos.boletas import Seleccion
from msa.core.led_action.constants import PREVIOUS_LED_ACTION
from msa.modulos import get_sesion
from msa.modulos.asistida import Modulo as ModuloAsistida
from msa.modulos.asistida.controlador import Controlador as ControllerAsistida
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.capacitacion.controlador import Controlador as ControllerCapac
from msa.modulos.capacitacion.rampa import RampaCapacitacion
from msa.modulos.constants import (E_REGISTRANDO, MODULO_ASISTIDA,
                                   MODULO_CAPACITACION, MODULO_INICIO,
                                   MODULO_SUFRAGIO, E_ESPERANDO,
                                   MODULO_CALIBRADOR)
from msa.modulos.sufragio import Modulo as ModuloSufragio
from msa.modulos.sufragio.constants import PANTALLA_INSERCION_BOLETA
from msa.modulos.sufragio.controlador import Controlador as ControllerVoto
from msa.modulos.sufragio.registrador import Registrador
from msa.core.exceptions import MesaIncorrecta

class FakeRegistrador(Registrador):
    """Registrador falso que se usa durante la capacitación para reemplazar al que es utilizado
    en el módulo de escrutinio."""

    def __init__(self, *args):
        """Constructor."""
        super(FakeRegistrador, self).__init__(*args[:4])

    def registrar_voto(self, solo_imprimir=False):
        """El registro del voto en capacitación expulsa la boleta en lugar
        de imprimir a la misma. Luego finaliza el registro del voto."""
        
        self.modulo.rampa.set_led_action('impresion')
        timeout_add(4000, self.modulo.rampa.expulsar_boleta)
        timeout_add(8000, self.modulo._fin_registro)

    def _prepara_impresion(self, seleccion):
        """Prepara la impresion del voto."""
        self.seleccion = seleccion


class Modulo(ModuloSufragio):
    """
    Módulo para capacitación de electores.

    Muestra un menú para elegir la ubicación (en caso de ser más de una) y permite
    elegir entre capacitar sufragio, asistida e imprimir votos en blanco para
    capacitar sobre la verificación del voto en caso de que esté activado.
    """

    def __init__(self, nombre):
        """Constructor."""
        self._mesa_anterior = None
        self.controlador = ControllerCapac(self)
        self.web_template = "capacitacion"

        ModuloBase.__init__(self, nombre)
        self.config_files = [COMMON_SETTINGS, MODULO_SUFRAGIO, MODULO_ASISTIDA,
                             nombre]
        self._load_config()
        self.estado = None

        self.constants_sent = False

        self.rampa = RampaCapacitacion(self)
        self.sesion = get_sesion()
        self._timeout_consulta = None
        self._consultando_tag = None

        self.time_last_tag = None

    def _set_controller(self):
        """
        Establece el controlador.
        """
        self.controlador = ControllerCapac(self)

    def imprimir_boleta(self):
        selec = Seleccion(self.controlador.mesa)
        selec.rellenar_de_blanco()
        registrador = Registrador(self.controlador.fin_boleta_demo, self,
                                  self.controlador.fin_boleta_demo_error)
        registrador.seleccion = selec
        # REVISAR, no estaba en 4.0, confío en PY porque se estuvo tocando capa
        self.set_estado(E_REGISTRANDO)
        registrador.registrar_voto()
        self.rampa.datos_tag = None

    def cancelar_impresion(self):
        """Establece el estado del módulo sufragio en :const:`E_ESPERANDO <modulos.constants.E_ESPERANDO>`."""
        self.set_estado(E_ESPERANDO)

    def _iniciar_capacitacion(self):
        """
        Método que inicia el módulo de capacitación.

        Se carga la pantalla web ``sufragio`` y se obtiene el controlador de voto.

        Dependiendo de la configuración que se tenga en la variable ``self.config("imprimir_capacitacion")`` utiliza
        :meth:`FakeRegistrador <modulos.capacitacion.FakeRegistrador>` o
        :meth:`Registrador <modulos.sufragio.registrador.Registrador>`.

        Luego muestra la ventana correspondiente.
        """
        self._descargar_ui_web()
        self.web_template = "sufragio"
        self.controlador = ControllerVoto(self)

        Clase_reg = Registrador if self.config("imprimir_capacitacion") \
            else FakeRegistrador
        self.registrador = Clase_reg(self._fin_registro, self, self._error)

        sleep(1)
        self._cargar_ui_web()
        sleep(1)
        self.ventana.show_all()
        self.estado = E_ESPERANDO

    def _iniciar_capacitacion_asistida(self):
        """
        Método que inicia el módulo de capacitación asistida.

        Se carga la pantalla web ``sufragio`` y se obtiene el controlador de voto.
        Utiliza :meth:`ModuloAsistida <modulos.asistida>` para inicializar el locutor y a
        :meth:`Controlador <modulos.asistida.controlador.Controlador>` como controlador del módulo de asistida.

        Dependiendo de la configuración que se tenga en la variable ``self.config("imprimir_capacitacion")`` utiliza
        :meth:`FakeRegistrador <modulos.capacitacion.FakeRegistrador>` o
        :meth:`Registrador <modulos.sufragio.registrador.Registrador>`.

        Luego muestra la ventana correspondiente.
        """
        self._descargar_ui_web()
        self.web_template = "sufragio"
        ModuloAsistida.inicializar_locutor(self)
        self.controlador = ControllerAsistida(self)

        Clase_reg = Registrador if self.config("imprimir_capacitacion") \
            else FakeRegistrador
        self.registrador = Clase_reg(self._fin_registro, self, self._error)

        sleep(1)
        self._cargar_ui_web()
        sleep(1)
        self.ventana.show_all()
        self.estado = E_ESPERANDO

    def _ready(self):
        """
        Envía las constantes y carga los botones cuando se cargó el HTML.
        """
        self.controlador.send_constants()
        self.controlador.cargar_botones()

    def _guardar_voto(self):
        """
        Guarda al voto. Establece el estado del módulo sufragio en
        :const:`E_REGISTRANDO <modulos.constants.E_REGISTRANDO>`.
        Luego imprime o no dependiendo del registrador que se haya establecido de acuerdo a la
        setting ``self.config("imprimir_capacitacion")``.
        No guarda datos en el tag.
        """
        self.set_estado(E_REGISTRANDO)
        self.registrador.registrar_voto(solo_imprimir=True)
        self.rampa.datos_tag = None

    def _configurar_ubicacion_capacitacion(self, ubicacion):
        """
        Establece la ubicación para capacitar.

        Args:
            ubicacion (str): Ubicación que se obtiene desde el front y que indica la ubicación sobre la que
                se llevará a cabo la capacitación.
        """
        mesa_obj = Ubicacion.one(id_unico_mesa=ubicacion)
        self._mesa_anterior = self.sesion.mesa
        mesa_obj.set_aes_key(b"\xff"*16)
        self.sesion.mesa = mesa_obj
        self._load_config()

    def salir(self):
        """
        Sale del módulo o va al menu de capacitación, segun el contexto.
        """
        if self.controlador.nombre == MODULO_CAPACITACION:
            if self._mesa_anterior:
                self.sesion.mesa = self._mesa_anterior
            self.rampa.expulsar_boleta()
            self._salir()
        else:
            self._descargar_ui_web()
            self.controlador = ControllerCapac(self)
            self.web_template = "capacitacion"
            self.rampa.set_led_action('reset')

            def _recargar():
                self._cargar_ui_web()
                self.ventana.show_all()
                self.rampa = RampaCapacitacion(self)

            idle_add(_recargar)

    def _salir(self):
        """Sale del módulo de capacitación, desloguea al usuario."""
        self.salir_a_modulo(MODULO_INICIO)

    def _consultar(self, tag_leido):
        """Permite consultar según el nombre del controlador por el tag leído al módulo de sufragio,
        o muestra por pantalla la boleta."""
        if self.controlador.nombre == MODULO_SUFRAGIO:
            ModuloSufragio._consultar(self, tag_leido)
        else:
            if self.rampa.tiene_papel:
                try:
                    self._mostrar_consulta(tag_leido)
                except MesaIncorrecta:
                    self.logger.error("El tag corresponde a una mesa de otro juego.")
                    self.expulsar_boleta("juego_datos")
                    self._fin_consulta()
                except Exception as err:
                    self.expulsar_boleta("excepcion")
                    self.logger.exception("ocurrió un error al parsear el tag.")
                    self._fin_consulta()
    
    def pantalla_insercion(self, cambiar_estado=True):
        """Muestra la pantalla de insercion de la boleta."""
        self.rampa.set_led_action('reset')
        if self.estado is None or self.estado == E_REGISTRANDO:
            # es None en la pantalla de la impresora
            # capacitación no debe encender leds de sufragio
            self.seleccion = None
            if cambiar_estado:
                self.set_estado(E_ESPERANDO)
            self.start_presencia()
            self.set_pantalla(PANTALLA_INSERCION_BOLETA)
        else:
            # sufragio
            super().pantalla_insercion()
    
    def encender_led_espera_boleta(self):
        self.rampa.set_led_action('solicitud_acta')

    def reset_leds(self):
        self.rampa.set_led_action('reset')
    
    def _calibrar_pantalla(self):
        """Llama al calibrador de la pantalla."""
        self.sesion.retornar_a_modulo = MODULO_CAPACITACION
        self.ret_code = MODULO_CALIBRADOR
        self.ventana.remove(self.browser)
        self.quit()
