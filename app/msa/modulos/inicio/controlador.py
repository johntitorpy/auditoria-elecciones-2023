"""Controlador del modulo inicio"""
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.inicio.constants import TEXTOS


class Controlador(ControladorBase):

    """Controller para el modulo inicio."""

    def __init__(self, modulo):
        """Constructir de el controlador inicio."""
        super(Controlador, self).__init__(modulo)
        self.set_actions(BaseActionController(self))
        self.textos = TEXTOS

    def document_ready(self, data):
        """Callback que se llama en el document.ready del browser."""
        self.modulo._inicio()
        self.modulo._pantalla_principal()
        self.validacion_boton(data)

    def modulo_prueba_equipo(self, data):
        self.modulo.a_prueba_equipo()

    def validacion_boton(self, data):
        if not self.sesion.modo_demo:
            self.hide_button_prueba_equipo(data)

    def hide_button_prueba_equipo(self, data={}):
        self.send_command("hide_icono_prueba_equipo")

    def show_button_prueba_equipo(self):
        self.send_command("show_icono_prueba_equipo")
