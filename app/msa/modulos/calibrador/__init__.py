#!/usr/bin/env python
"""Módulo que permite la calibración de la máquina."""
from os import getenv, system

from msa.modulos.base.modulo import ModuloBase
from msa.modulos.calibrador.controlador import Controlador
from msa.modulos.calibrador.helpers.calibrador import Calibrador
from msa.modulos.constants import MODULO_INICIO, MODULO_MENU, MODULO_SUFRAGIO
from msa.modulos.gui.settings import SCREEN_SIZE


class Modulo(ModuloBase):

    """Módulo de calibración de pantalla."""

    def __init__(self, nombre):
        """
        Constructor de la clase.
        Se establecen los atributos con los que iniciará el módulo.
        Se utilizan las clases
        :meth:`Calibrador <modulos.calibrador.helpers.calibrador.Calibrador>`
        y
        :meth:`Controlador <modulos.calibrador.controlador.Controlador>`.
        Para las medidas de la pantalla utiliza
        :meth:`SCREEN_SIZE <modulos.gui.settings.SCREEN_SIZE>`.


        Args:
            nombre (str): nombre del módulo.
        """
        self.calibrador = Calibrador()
        width, height = SCREEN_SIZE
        self.calibrador.set_screen_prop(width, height)

        self.controlador = Controlador(self)
        self.web_template = "calibrador"

        # Esto hace que no se apague la pantalla
        system("DISPLAY=%s xset s off; xset -dpms" % getenv("DISPLAY", ":0"))

        ModuloBase.__init__(self, nombre)

    def reiniciar(self):
        """Reinicia el calibrador."""
        self.calibrador.reiniciar()

        punto_verificacion = self.obtener_punto_verficacion()
        self.controlador.reiniciar(punto_verificacion)

    def calibrar(self, datos_calibracion):
        """
        Lleva a cabo las acciones para la calibración.
        Primero registra clicks utilizando los datos recibidos y el método
        :meth:`registrar_clicks <modulos.calibrador.helpers.calibrador.Calibrador.registrar_clicks>`.
        Luego calibra ejes utilizando el método
        :meth:`calibrar_ejes <modulos.calibrador.helpers.calibrador.Calibrador.calibrar_ejes>`.

        Args:
            datos_calibracion (?): Datos de calibración.

        """
        self.calibrador.registrar_clicks(datos_calibracion)
        self.calibrador.calibrar_ejes()

    def obtener_punto_verficacion(self):
        """
        Devuelve un punto de verificación utilizando
        :meth:`generar_punto_verificacion <modulos.calibrador.helpers.calibrador.Calibrador.generar_punto_verificacion>`.

        Returns:
            Tuple[int, int]:
            Coordenadas x,y del punto de verificación.
        """
        return self.calibrador.generar_punto_verificacion()

    def quit(self, w=None):
        """Sale del modulo."""
        if self.sesion.retornar_a_modulo:
            self.ret_code = self.sesion.retornar_a_modulo
        elif self.sesion._mesa is not None:
            self.ret_code = MODULO_MENU
        else:
            self.ret_code = MODULO_INICIO
        self._descargar_ui_web()
        ModuloBase.quit(self)
        self.sesion.retornar_a_modulo = False
