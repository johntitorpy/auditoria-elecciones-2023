"""Contiene el controlador base para la interaccion con la web view."""
from os import popen
from zaguan import WebContainerController

from msa.core.data.helpers import get_config
from msa.core.data.settings import JUEGO_DE_DATOS
from msa.modulos import get_sesion
from msa.modulos.constants import (EXT_IMG_VOTO, PATH_FOTOS_ORIGINALES,
                                   PATH_TEMPLATES_MODULOS, PATH_TEMPLATES_VAR,
                                   PATH_TEMPLATES_FLAVORS)
from msa.modulos.gui.settings import MOSTRAR_CURSOR
from msa.settings import DEBUG


class ControladorBase(WebContainerController):
    """
        Controlador base para los controladores de todos los modulos.

        Attributes:
            modulo (modulos.base.modulo.ModuloBase): referencia al modulo.
            sesion (modulos.Sesion): sesion actual.
            textos (List[str]): lista de textos a mostrar en pantalla.
            _callback_aceptar (function): la funcion que se llama al procesar el dialogo si la respuesta fué afirmativa.
            _callback_cancelar (function):
                la funcion que se llama al procesar el dialogo si la respuesta fué afirmativa.

    """

    def __init__(self, modulo):
        """
        Obtiene la sesion y linkea al modulo.

        Args:
            modulo (modulos.base.modulo.ModuloBase): modulo a enlazar.
        """
        WebContainerController.__init__(self)
        self.modulo = modulo
        self.sesion = get_sesion()

        self._callback_aceptar = None
        self._callback_cancelar = None
        self.textos = None

    def get_browser(self, *args, **kwargs):
        """
        Extiende: :meth:`zaguan.controller.WebContainerController.get_browser`.
        Si :const:`DEBUG <settings.DEBUG>` = True entonces configura el browser para debuggear.

        Args:
            *args:
                se pasan a
                :meth:`WebContainerController.get_browser() <zaguan.controller.WebContainerController.get_browser>`
            **kwargs:
                se pasan a
                :meth:`WebContainerController.get_browser() <zaguan.controller.WebContainerController.get_browser>`

        Returns:
            WebKit2.WebView
        """
        browser = super().get_browser(*args, **kwargs)
        if DEBUG:
            self.send_function("zaguan_logging = true;")
            self.send_function("console.log('Depurando JS', zaguan_logging);")
        return browser

    def cargar_dialogo(self, callback_template, aceptar=None, cancelar=None):
        """
        Ejecuta la funcion :ref:`js.popup.cargar_dialogo() <js.popup.cargar_dialogo>` del frontend.

        Enlaza:

        - ``aceptar`` con :attr:`_callback_aceptar <ControladorBase._callback_aceptar>`.
        - ``cancelar`` con :attr:`_callback_cancelar <ControladorBase._callback_cancelar>`.

        Args:
            callback_template (str):
                nombre de la funcion que debe llamar el front end luego de ejecutar ``cargar_dialogo``
            aceptar:
                el objeto ``function`` a enlazar con :attr:`_callback_aceptar <ControladorBase._callback_aceptar>`.
            cancelar:
                el objeto ``function`` a enlazar con :attr:`_callback_cancelar <ControladorBase._callback_cancelar>`

        """
        self._callback_aceptar = aceptar
        self._callback_cancelar = cancelar
        self.send_command("cargar_dialogo", callback_template)

    def procesar_dialogo(self, respuesta_afirmativa):
        """
        Procesa la accion tomada en el dialogo. Si es ``true`` llama a :attr:`ControladorBase._callback_aceptar` sino
        a :attr:`ControladorBase._callback_cancelar`.
        Finalmente, limpia las funciones asociadas a los callbacks de aceptar y cancelar.

        Args:
            respuesta_afirmativa (bool): tipo de respuesta

        """
        self.modulo.play_sonido_tecla()
        callback_dialogo = None
        if respuesta_afirmativa:
            if self._callback_aceptar is not None:
                callback_dialogo = self._callback_aceptar
        else:
            if self._callback_cancelar is not None:
                callback_dialogo = self._callback_cancelar

        self._callback_aceptar = None
        self._callback_cancelar = None

        if callback_dialogo is not None:
            callback_dialogo()

    def set_actions(self, action):
        """
        Enlaza un procesador a la clave ``voto``.

        Args:
            action (zaguan.actions.BaseActionController): el procesador a enlazar.

        .. seealso::

            Funcion de zaguan que agrega procesadores :meth:`zaguan.controller.WebContainerController.add_processor`


        """
        self.add_processor("voto", action)

    def do_click(self, selector):
        """
        Ejecuta un click en un elemento del browser obtenido con JQuery a partir de un ``selector``.
        Args:
            selector (str):  el selector que va a usar JQuery.

        """
        self.send_function('document.querySelector("{}").click()'.format(selector))

    def do_set_value(self, selector, value):
        """
        Establece un valor (``value``) en el elemento del browser obtenido por un selector (``selector``).

        Args:
            selector (str): el selector
            value (str): el valor a establecer
        """
        self.send_function('document.querySelector("{}").value = "{}"'.format(selector, value))

    def hide_dialogo(self):
        """Oculta el dialogo."""
        self.send_command("hide_dialogo")

    def get_encabezado(self):
        """Devuelve los datos de configuracion para la clave ``datos_eleccion``"""
        return get_config("datos_eleccion")

    def base_constants_dict(self):
        """
        Genera un diccionario con constantes. Las claves a establecer son:

        .. code-block::

            {
                "encabezado": {texto: encabezado[texto] for texto in encabezado},
                "ext_img_voto": EXT_IMG_VOTO,
                "flavor": flavor,
                "juego_de_datos": JUEGO_DE_DATOS,
                "mostrar_cursor": MOSTRAR_CURSOR,
                "PATH_TEMPLATES_MODULOS": "file:///%s/" % PATH_TEMPLATES_MODULOS,
                "PATH_TEMPLATES_FLAVORS": "file:///%s/" % PATH_TEMPLATES_FLAVORS,
                "PATH_TEMPLATES_VAR": "file:///%s/" % PATH_TEMPLATES_VAR,
                "path_imagenes_candidaturas": "file:///%s/" % PATH_FOTOS_ORIGINALES,
            }

        Returns:
            dict: diccionario con las constantes.

        """
        flavor = self.modulo.config("flavor")
        encabezado = self.get_encabezado()
        constants_dict = {
            "encabezado": {texto: encabezado[texto] for texto in encabezado},
            "ext_img_voto": EXT_IMG_VOTO,
            "flavor": flavor,
            "juego_de_datos": JUEGO_DE_DATOS,
            "mostrar_cursor": MOSTRAR_CURSOR,
            "mostrar_ubicacion": self.modulo.config("mostrar_ubicacion_en_header"),
            "PATH_TEMPLATES_MODULOS": "file:///%s/" % PATH_TEMPLATES_MODULOS,
            "PATH_TEMPLATES_FLAVORS": "file:///%s/" % PATH_TEMPLATES_FLAVORS,
            "PATH_TEMPLATES_VAR": "file:///%s/" % PATH_TEMPLATES_VAR,
            "path_imagenes_candidaturas": "file:///%s/" % PATH_FOTOS_ORIGINALES,
        }
        if self.textos is not None:
            constants_dict["i18n"] = {trans: _(trans) for trans in self.textos}

        return constants_dict

    def send_constants(self):
        """Envía todas las constantes de la eleccion al browser."""
        constants_dict = self.get_constants()
        self.send_command("set_constants", constants_dict)

    def get_constants(self):
        """
        Obtiene las constantes y las devuelve

        Returns:
            dict: diccionario con las constantes.
        """
        constants_dict = self.base_constants_dict()
        return constants_dict

    def encender_pantalla(self):
        """
        Envía el comando para encender la pantalla.
        """
        self.modulo.rampa.set_backlight_status(True)

    def apagar_pantalla(self):
        """
        Envía el comando para apagar la pantalla.
        """
        self.modulo.rampa.set_backlight_status(False)

    def _get_set_brightness_command(self, curr_brightness_level):
        get_primary_monitor_command = "$(echo $(xrandr --listactivemonitors | grep '0: ' | awk '{print $4}'))"
        set_brightness_command = "xrandr --output {} --brightness {}"
        return set_brightness_command.format(get_primary_monitor_command, curr_brightness_level / 100)

    def set_specific_brightness(self, brightness):
        """
        Establece el brillo que se recibe por parámetro. Por defecto
        el valor será el brillo por defecto que se tiene en la variable 
        ``DEFAULT_BRIGHTNESS``
        
        Args:
            brightness (int): Valor del brillo que se seteará.
        """
        popen(self._get_set_brightness_command(brightness))
    
    def get_brightness(self):
        """Devuelve el brillo de la pantalla."""
        if self.rampa.tiene_conexion:
            brightness = self.rampa.get_actual_brightness()
            if brightness is not None:
                self.brightness_level = int(brightness)

    def mostrar_div_presencia(self):
        """
        Solicito al front que muestre el div invisible que enmascara el click
        cuando la pantalla se esta por apagar.
        """
        self.send_command("mostrar_div_presencia")

    def ocultar_div_presencia(self):
        """
        Solicito al front que saque el div para que el usuario pueda interacturar
        con el módulo.
        """
        self.send_command("ocultar_div_presencia")

    def presence_reset(self, value):
        self.modulo.rampa.presence_reset(value)
