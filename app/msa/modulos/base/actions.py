"""Contiene la clase base para el manejo de las Actions de Zaguan."""
from zaguan.actions import BaseActionController as ZaguanAction
from zaguan.functions import asynchronous_gtk_message


class BaseActionController(ZaguanAction):
    """
    Controlador de Acciones Basico para los modulos.
    """

    def __init__(self, controlador):
        """
        Establece el enlace con el controlador.
        Args:
            controlador (modulos.base.controlador.ControladorBase): el controlador.
        """
        ZaguanAction.__init__(self, controlador)
        self.controlador = controlador

    def log(self, data):
        """
        Loguea desde la UI.

        Args:
            data (str): datos a logear

        """
        self.controlador.sesion.logger.debug("LOG >>>%s" % data)

    def respuesta_dialogo(self, data):
        """
        Llama a :meth:`modulos.base.controlador.ControladorBase.procesar_dialogo` con los datos que se pasan como
        parámetros.

        Args:
            data (bool):  tipo de respuesta

        """
        self.controlador.procesar_dialogo(data)

    def document_ready(self, data):
        """
        Ejecuta la funcion ``document_ready`` de los controladores. Si el controlador tiene implementada la funcion
        ``_after_ready`` la ejecuta tambien.

        Args:
            data (any): parámetros para ejecutar la funcion del controlador.

        """
        self.controlador.document_ready(data)
        # usado para el testing framework
        if hasattr(self.controlador, "_after_ready"):
            self.call_async(self.controlador._after_ready)

    def volver(self, data):
        """
        Accion para el botón volver. Ejecuta el método ``volver`` en el módulo.
        """
        self.controlador.modulo.volver()

    def salir(self, data):
        """Lllama al metodo salir del módulo."""
        self.controlador.modulo.salir()

    def administrador(self, data):
        """Lllama a la salida al administrador."""
        self.controlador.modulo.administrador()

    def call_async(self, func, params=None):
        """
        Ejecuta la funcion que se pasa con sus parámetros de forma asíncrona.

        Args:
            func (function): la funcion a ejecutar.
            params (tuple): los parámetros a pasar a la función.

        """
        async_func = asynchronous_gtk_message(func)
        if params is not None:
            async_func(params)
        else:
            async_func()

    def sonido_tecla(self, data):
        """Reproduce el sonido de tecla"""
        self.controlador.modulo.play_sonido_tecla()

    def sonido_error(self, data):
        """Reproduce el sonido de error"""
        self.controlador.modulo.play_sonido_error()

    def sonido_warning(self, data):
        """Reproduce el sonido de advertencia"""
        self.controlador.modulo.play_sonido_warning()

    def sonido_ok(self, data):
        """Reproduce el sonido OK"""
        self.controlador.modulo.play_sonido_ok()

    def registrar_presencia_touch(self, data):
        self.controlador.modulo.rampa.presence_reset(True)
