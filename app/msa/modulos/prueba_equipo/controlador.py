from gi.repository.GObject import timeout_add
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.prueba_equipo.constants import CDQC_LITE_ISO_GENERICA
from msa.modulos.prueba_equipo.constants import TEXTOS

from msa.core.logging import get_logger

logger = get_logger("helpers")


class Controlador(ControladorBase):

    """Controller para las pantallas de ingreso de datos."""

    def __init__(self, modulo):
        """Constructor del controlador de interaccion."""
        super(Controlador, self).__init__(modulo)
        self.set_actions(BaseActionController(self))
        self.textos = TEXTOS

    def document_ready(self, data):
        """Callback que llama el browser en el document.ready()"""
        self._inicializa_pantalla()

    def _inicializa_pantalla(self):
        """
        Prepara la primera pantalla de la interacción ocultando todos
        los elementos innecesarios del template y mostrando la imagen de la
        boleta.
        """
        self.send_constants()
        self.set_pantalla()
        self.modulo.default_value()
        self.modulo.rampa.expulsar_boleta()

    def set_prueba_equipo(self):
        """Muestra la pantalla de prueba de equipo."""
        mensaje = _("prueba_equipo")
        self.send_command("pantalla_prueba_equipo", {"mensaje": mensaje})

    def set_pantalla(self, data=None):
        """Setea la pantalla de acuerdo al estado actual."""
        if data is None:
            data = {}

        self.set_prueba_equipo()

        self.send_constants()

    def get_constants(self):
        """Genera las constantes propias de cada modulo."""
        local_constants = {"textos": TEXTOS}
        constants_dict = self.base_constants_dict()
        constants_dict.update(local_constants)
        return constants_dict

    def imprimir_boleta(self):
        """Realiza el test de impresion."""
        tipo_tag = "PruebaEquipo"
        seleccion_tag = ""
        self.send_command("pantalla_impresion_boleta")
        self.modulo.rampa.imprimir_serializado(tipo_tag, seleccion_tag, transpose=False)

    def boleta_detectada(self):
        """
        Funcion que llama a la pantalla cuando se detecta la boleta
        """

        data = {
            "error": True,
            "status": True,
            "grabando_chip": False,
            "mensaje": "¡Boleta detectada!",
        }
        self.send_command("pantalla_paso_2", data)

    def boleta_grabando_chip(self):
        """
        Funcion que llama a la pantalla cuando se ha grabado el chip correctamente
        """

        data = {
            "error": True,
            "status": True,
            "grabando_chip": True,
            "mensaje": "Grabando chip...",
        }
        self.send_command("pantalla_paso_2", data)

    def boleta_tag_grabado(self):
        """
        Funcion que llama a la pantalla cuando NO se ha grabado el chip correctamente
        """

        data = {
            "error": False,
            "status": True,
            "grabando_chip": False,
            "mensaje": "¡Boleta insertada con chip grabado!",
        }
        self.send_command("pantalla_paso_2", data)

    def boleta_tag_roto(self):
        """
        Funcion que llama a la pantalla cuando la boleta insertada se encuentras sin chip
        """

        data = {
            "error": False,
            "status": True,
            "grabando_chip": False,
            "mensaje": "¡Boleta insertada sin chip (tag roto)!",
        }
        self.send_command("pantalla_paso_2", data)

    def boleta_tag_grabar(self):
        """
        Funcion que llama a la pantalla cuando se manda a graba chip
        """

        data = {
            "error": True,
            "status": True,
            "grabando_chip": False,
            "mensaje": "¡El chip se grabó con éxito!",
        }
        self.send_command("pantalla_paso_2", data)

    def boleta_tag_error_grabar(self):
        """
        Funcion que llama a la pantalla cuando hubo un error al grabar el chip
        """

        data = {
            "error": True,
            "status": False,
            "grabando_chip": False,
            "mensaje": "¡No se pudo grabar el chip!",
        }
        self.send_command("pantalla_paso_2", data)

    def impresion_boleta(self):
        """
        Funcion que se llama cuando se imprime boleta
        """

        data = {"status": True, "mensaje": "¡La boleta se imprimió correctamente!"}
        self.send_command("pantalla_resultado_impresion_boleta", data)

    def error_impresion_boleta(self):
        """
        Funcion que se llama cuando NO se pudo imprimir la boleta
        """

        data = {"status": False, "mensaje": "¡No se pudo imprimir la boleta!"}
        self.send_command("pantalla_resultado_impresion_boleta", data)

    def paso_pantalla_verificar_imagen(self, data):

        self.modulo.cambiar_estado_verificar_imagen()
        self.send_command("pantalla_paso_3")

    def cambio_estado_pantalla_popup(self, data):
        self.modulo.cambio_estado_popup()

    def paso_pantalla_verificar(self, data):
        """
        Da paso a pantalla para que acerque la boleta a la antena
        """

        self.modulo.cambio_estado_verificando_tag()
        self.send_command("pantalla_paso_4")
        self.modulo._lanzar_timeout_verificacion_tag()

    def cambio_estado_repetir_prueba_validacion(self, data):
        # self.registrar_lector(data)
        self.modulo.cambio_estado_verificando_tag()

    def apagar_equipo(self, data):
        """
            Envía la orden de apagado de la máquina.
        """
        self.modulo.apagar()

    def popup(self):
        """
        Funcion que carga la pantalla de popUP
        """

        self.send_command("cargar_popup")

    def confirmacion_popup_validacion_chip(self, data=None):
        """
        Llama a la funcion que tira timer para el PopUp
        """
        self.modulo.cambio_estado_verificando_tag()
        self.modulo._lanzar_timeout_verificacion_tag()

    def cancelacion_popup_validacion_chip(self, data=None):
        self.modulo._remover_timeout_verificacion_tag()

    def validacion_chip(self):
        """
        Pantalla de validacion del chip boleta
        """

        self.modulo._remover_timeout_verificacion_tag()
        # self.modulo.rampa.desregistrar_lector()
        self.send_command("pantalla_paso_5")

    def error_lectura_chip(self, data=None):
        """
        Pantalla de error en la validacion el chip boleta
        """
        data = {"CDQC_LITE_ISO_GENERICA": CDQC_LITE_ISO_GENERICA, "cancel_popup": False}
        self.modulo.cambiar_estado_error_validacion()
        self.modulo._remover_timeout_verificacion_tag()
        # self.modulo.rampa.desregistrar_lector()
        self.send_command("error_leer_chip", data)

    def paso_cancelar_popup(self, data=None):
        """
        Pantalla de que llama al error de chip luego de presionar cancelar dentro del popup
        """
        data = {"CDQC_LITE_ISO_GENERICA": CDQC_LITE_ISO_GENERICA, "cancel_popup": True}
        self.modulo.cambiar_estado_error_validacion()
        self.modulo._remover_timeout_verificacion_tag()
        # self.modulo.rampa.desregistrar_lector()
        self.send_command("error_leer_chip", data)

    def paso_pantalla_final(self, data):
        """
        Da un tiempo para pasar las ultima 2 pantallas
        """
        self.modulo.cambio_estado_tag_validado()
        timeout_add(3000, self._paso_pantalla_6, data)
        self.registrar_lector(data)

    def _paso_pantalla_6(self, data):
        data = {
            "CDQC_LITE_ISO_GENERICA": CDQC_LITE_ISO_GENERICA,
        }
        self.send_command("pantalla_paso_6", data)
        self.modulo.rampa.expulsar_boleta("Validacion finalizada")

    def reinicio_pantallas(self, data):
        """
        Vuelve a la pantalla principal y deja todo en
        """

        self.modulo.default_value()
        # self.registrar_lector(data)
        self.send_command("pantalla_prueba_equipo")

    def registrar_lector(self, data):
        """
        Llama a la funcion que tira timer para el PopUp
        """

        self.modulo.rampa.registrar_eventos()

    def salir(self):
        self.modulo.salir()
        self.send_command("pantalla_paso_6", data)
        self.modulo.rampa.expulsar_boleta("Validacion finalizada")

    def registrar_lector(self, data):
        """
        Llama a la funcion que tira timer para el PopUp
        """

        self.modulo.rampa.registrar_eventos()

    def reinicio_modulo(self, data):
        self.modulo.reiniciar_modulo()

    def salir(self, data):
        self.modulo.salir()
