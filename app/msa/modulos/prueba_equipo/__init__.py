"""
Modulo que maneja el ingreso de datos de los usuarios.

Maneja 3 pantallas distintas:
    * Introduccion de mesa y pin (usado en modulo Inicio)
    * Introduccion de datos personales (usado en Apertura y Escrutinio)
    * Pantalla de insercion de acta (usado en Apertura, pero soporta todos los
      tipos de acta)
"""

from gi.repository.GObject import timeout_add, source_remove, idle_add

from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.modulos import get_sesion
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.prueba_equipo.constants import (
    E_IMPRIMIENDO,
    E_IMPRESION_FINALIZADA,
    E_VERIFICACION_TAG,
    E_ERROR_VERIFICACION_TAG,
    E_VALIDADO,
    E_ESPERANDO_BOLETA,
    E_ERROR_IMPRESION,
    E_VERIFICACION_IMAGEN,
    E_POPUP,
    E_ERROR_GRABAR_CHIP,
    E_BOLETA_QUEMADA,
    E_GRABANDO_TAG,
    E_INICIALIZANDO,
)
from msa.modulos.constants import MODULO_INICIO, SHUTDOWN
from msa.modulos.prueba_equipo.controlador import Controlador
from msa.modulos.prueba_equipo.rampa import Rampa
from msa.core.logging import get_logger

logger = get_logger("MODULO_PRUEBA_EQUIPO")


class Modulo(ModuloBase):

    """Modulo de ingreso de datos.
    Este modulo funciona como submodulo de Inicio, Apertura y Recuento.
    Muestra las siguientes 3 "pantallas":
        * Ingreso de Mesa y PIN
        * Ingreso de Datos Personales
        * Ingreso de Actas y Certificados
    """

    def __init__(self, nombre):
        """Constructor."""
        self.nombre = nombre
        self.sesion = get_sesion()
        self.estado = E_INICIALIZANDO

        self.web_template = "prueba_equipo"
        self.sesion.logger.info(self.nombre)

        # Pantalla de introduccion de mesa y pin del modulo Inicio
        # self.rampa = RampaCopiasCertificado(self)
        self.controlador = Controlador(self)
        ModuloBase.__init__(self, nombre, activar_presencia=False)

        self.rampa = Rampa(self)

        self._timer_verificador_tag = None

        # self.rampa.set_led_action('espera_en_antena')
        self.config_files = [COMMON_SETTINGS, "prueba_equipo"]
        self._load_config()
        self._start_audio()

    def document_ready(self):
        """Inicializamos cuando el browser tira el evento de document ready."""
        # Mandamos las constantes que el modulo necesita para operar.
        self.controlador.send_constants()
        # llamamos al maestro de ceremonias de la rampa para que evalúe como
        # proceder
        self.rampa.maestro()

    def pantalla_inicial(self):
        self.estado = E_ESPERANDO_BOLETA
        self.controlador.send_constants()
        self.controlador.set_pantalla()
        self.rampa.expulsar_boleta()

    def set_pantalla(self, pantalla):
        """Setea la pantalla indicada."""
        self.controlador.set_screen(pantalla)

    def boleta_impresa_correctamente(self):
        """Impresion."""
        self.cambio_estado_fin_impresion()
        self.controlador.impresion_boleta()

    def error_boleta_impresion(self):
        """Error en la impresion."""
        self.estado = E_ERROR_IMPRESION
        self.controlador.error_impresion_boleta()

    def tag_grabado(self):
        """Tag grabado."""
        self.estado = E_ERROR_GRABAR_CHIP
        self.controlador.boleta_tag_grabado()

    def tag_roto(self):
        """Tag roto."""

        self.controlador.boleta_tag_roto()

    def boleta_detectada(self):
        """Tag vacio."""

        self.controlador.boleta_detectada()

    def boleta_grabando_chip(self):
        """Tag vacio."""

        self.estado = E_GRABANDO_TAG
        self.controlador.boleta_grabando_chip()

    def tag_grabado_correctamente(self):
        """Tag grabado correctamente."""

        self.estado = E_BOLETA_QUEMADA
        self.controlador.boleta_tag_grabar()

    def tag_error_grabar(self):
        """Error al grabar tag."""

        self.estado = E_ERROR_GRABAR_CHIP
        self.controlador.boleta_tag_error_grabar()

    def imprimir_boleta(self):
        """Imprime una boleta de prueba"""

        self.estado = E_IMPRIMIENDO
        self.controlador.imprimir_boleta()

    def pantalla_validacion(self):
        """Imprime una boleta de prueba"""

        self.controlador.validacion_chip()

    def _lanzar_timeout_verificacion_tag(self, leido=False):
        if self.estado == E_VERIFICACION_TAG:

            def _verificar_tag_leido():
                """Callback en segundo plano para chequear el tag"""
                self.cambio_estado_popup()
                self.pantalla_popup()

            self.rampa.registrar_lector()
            self._timer_verificador_tag = timeout_add(21000, _verificar_tag_leido)

    def _remover_timeout_verificacion_tag(self):
        if (
            self.estado in (E_VERIFICACION_TAG, E_ERROR_VERIFICACION_TAG, E_VALIDADO)
            and self._timer_verificador_tag is not None
        ):

            source_remove(self._timer_verificador_tag)
            self._timer_verificador_tag = None

    def pantalla_popup(self):
        """pantalla que muestra popup"""
        self.controlador.popup()

    def pantalla_error_lectura_chip(self):
        """pantalla que muestra error de lectura del chip"""
        self.controlador.error_lectura_chip()

    def apagar(self):
        """Sale del módulo de inicio y envia la orden de apagado """
        self.ret_code = SHUTDOWN
        idle_add(self.quit)

    def salir(self):
        self.salir_a_menu()

    def default_value(self):
        logger.info("DEFAULT VALUE")
        self.estado = E_ESPERANDO_BOLETA
        self.rampa.tag_generado = None

    def cambio_estado_esperando_boleta(self):
        self.estado = E_ESPERANDO_BOLETA

    def cambio_estado_fin_impresion(self):
        self.estado = E_IMPRESION_FINALIZADA

    def cambio_estado_verificando_tag(self):
        self.estado = E_VERIFICACION_TAG

    def cambio_estado_tag_validado(self):
        self.estado = E_VALIDADO

    def cambiar_estado_verificar_imagen(self):
        self.estado = E_VERIFICACION_IMAGEN

    def cambio_estado_popup(self):
        self.estado = E_POPUP

    def cambiar_estado_error_validacion(self):
        self.estado = E_ERROR_VERIFICACION_TAG

    def reiniciar_modulo(self):
        """Sale del módulo, vuelve al comienzo con la maquina
        desconfigurada.
        """
        print("llama a reiniciar el modulo")
        self.quit()

    def salir_a_menu(self):
        """Sale del módulo de apertura, vuelve al comienzo con la maquina
        desconfigurada.
        """
        print("llama a salir a menu de inicio")
        self.salir_a_modulo(MODULO_INICIO)

    def pantalla_insercion(self):
        pass
