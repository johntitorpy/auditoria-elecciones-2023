import gi

# Si no Establecemos explicitamente las versiones de los modulos del
# repositorio de pygi muestra un warning
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
# Establecemos la version de WebKit (API 3.0)
try:
    gi.require_version("WebKit", "3.0")
except ValueError:
    pass
# Establecemos la version de WebKit (API 4.0)
try:
    gi.require_version("WebKit2", "4.0")
except ValueError:
    pass

from os.path import exists, join
from time import sleep
from urllib.request import pathname2url
from gi.repository import Gdk, GObject, Gtk
from gi.repository.GObject import timeout_add
from msa.core.audio.player import AudioPlayer
from msa.core.config_manager import Config
from msa.core.i18n import cambiar_po
from msa.modulos import get_sesion
from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.modulos.base.plugins import PluginManager
from msa.modulos.constants import (
    APP_TITLE,
    MODULO_MENU,
    PATH_SONIDOS_VOTO,
    PATH_TEMPLATES_MODULOS,
    WINDOW_BORDER_WIDTH,
    PATH_MODULOS,
)
from msa.modulos.gui.settings import (
    DEBUG_ZAGUAN,
    FULLSCREEN,
    MOSTRAR_CURSOR,
    SCREEN_SIZE,
    WEBKIT_VERSION,
    USAR_SONIDOS_UI,
)
from msa.modulos.base.decorators import presencia_on_required

# Hilo Global del módulo para reproducir sonidos
_audio_player = None


def print_zaguan_input(msg):
    """
    En base al mensaje que le llegue, se lo trata
    para que sea apto para Zaguan.

    Args:
        msg (str): Mensaje que debe ser tratado.

    Returns:
         str: Con el formato que admite Zaguan.
    """
    from ujson import loads
    from re import search
    from pprint import pprint

    exp = "(run_op)\\(['\"](\\w+)['\"], ['\"](.*)['\"]\\)"
    matches = search(exp, msg)
    if matches is not None:
        groups = matches.groups()
        if groups[0] == "run_op":
            comando = groups[1]
            json_str = groups[2]
            print(">>>", comando)
            if comando == "set_constants":
                pprint(loads(json_str), depth=1)
            elif json_str != "null":
                print("\t", json_str[:80], "..." if len(json_str) > 80 else "")

        else:
            print(msg)
    else:
        print(msg)


class ModuloBase(object):
    """
    Modulo base. Implementa una pantalla y la funcionalidad basica.

    Attributes:
        sesion (modulos.Sesion): sesion de la aplicacion
        logger (logging.Logger): logger
        config_files (list[str]): lista de nombres de archivos de donde se tomarán configuraciones.
        nombre (str): nombre del módulo.
        pantalla (any):
        ret_code (str): valor que se retornará al finalizar la ejecucion del módulo.
        signal (any):
        player (any):
        plugin_manager (modulos.base.plugins.PluginManager): el administrador de plugins.
        ventana (Gtk.Window): la ventana donde se muestra el módulo.
    """

    def __init__(self, nombre, activar_presencia=False):
        """
        Obtiene la sesion, establece el nombre del módulo, inicializa la ventana y carga el browser. Finalmente muestra
        todo.

        Args:
            nombre (str): nombre del módulo.
        """
        self.sesion = get_sesion()
        self.logger = self.sesion.logger
        self.logger.info("Cargando modulo {}".format(nombre))

        self.activar_presencia = activar_presencia
        # Para la atenuacion de pantalla en modo presencia activada
        self.atenuacion_checks = 0
        self.presencia = False
        self.timer_timeout_ms = 500
        self.atenuacion_ms = 5000
        self.estado_leds = None

        self.config_files = [COMMON_SETTINGS, nombre]
        self._load_config()
        self.nombre = nombre
        self.pantalla = None
        self.ret_code = ""
        self.signal = None
        self.player = None
        self.plugin_manager = PluginManager
        self.plugin_manager.autoregister()

        self._set_controller()

        self.ventana = self._inicializa_ventana()
        self._cargar_ui_web()
        sleep(0.2)
        self.ventana.show_all()

    def cambiar_po(self, nombre_po):
        """
        Cambia el idioma de los mensajes.

        Args:
            nombre_po (str): nombre del archivo PO que se encuentra en la carpeta de locale.

        """
        cambiar_po(nombre_po)

    def _set_controller(self):
        pass

    def _inicializa_ventana(self):
        """
        Inicializa la ventana básica, tamaño, layout básico y títulos.

        Returns:
            Gtk.Window: la ventana
        """
        ventana = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        ventana.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        ventana.set_size_request(*SCREEN_SIZE)
        ventana.set_resizable(False)
        ventana.set_support_multidevice(False)

        ventana.set_title(APP_TITLE)
        ventana.set_border_width(WINDOW_BORDER_WIDTH)

        ventana.connect("destroy", self.quit)

        root_wnd = ventana.get_root_window()
        if MOSTRAR_CURSOR:
            cursor_type = Gdk.CursorType.LEFT_PTR
        else:
            cursor_type = Gdk.CursorType.BLANK_CURSOR

        cursor = Gdk.Cursor(cursor_type)
        root_wnd.set_cursor(cursor)

        if FULLSCREEN:
            ventana.fullscreen()

        self.logger.debug("Fin de inicializacion ventana")
        return ventana

    def _get_uri(self):
        """
        Genera y devuelve la URI del template web del módulo

        Returns:
            str: La URI del modulo.
        """
        html_name = "{}.html".format(self.web_template)
        file_ = join(PATH_TEMPLATES_MODULOS, html_name)
        uri = "file://" + pathname2url(file_)
        return uri

    def get_browser(self, uri):
        """
        Le pide al controlador el browser y lo retorna.

        Args:
            uri (str):

        Returns:
            WebKit2.WebView: el browser.

        """
        debug_callback = print_zaguan_input if DEBUG_ZAGUAN else None
        return self.controlador.get_browser(
            uri,
            debug=DEBUG_ZAGUAN,
            webkit_version=WEBKIT_VERSION,
            debug_callback=debug_callback,
        )

    def _webkit2_touch(self, widget, event):
        """Webkitgtk 2 no lanza el evento del DOM touchend y touchmove por un
        bug https://bugs.webkit.org/show_bug.cgi?id=158531 Por lo tanto muchos
        clicks no son capturados correctamente.

        Esta función intenta parchear el comportamiento y emitir el click
        cuando la persona hace algo con el dedo que no sea "el típico click
        con la punta del dedo". La mayoría de los clicks con la yema entran en
        por este camino.
        """
        # Agarro el evento de inicio del touch y guardo x, y timestamp
        if event.touch.type == Gdk.EventType.TOUCH_BEGIN:
            self.last_start = (event.x, event.y, event.get_time())
        elif event.touch.type == Gdk.EventType.TOUCH_END:
            # Establezco la diferencia para los dos ejes
            dx = abs(self.last_start[0] - event.x)
            dy = abs(self.last_start[1] - event.y)
            # si hubo algun evento de touch start (que debería siempre haber) y
            # los dedos se movieron menos de 20 pixeles en ambas direcciones
            if self.last_start is not None and dx < 20 and dy < 20:
                # en alguno de los dos ejes el dedo de tiene que haber movido
                # al menos dos pixeles
                dist_diff = dx > 2 or dy > 2
                time_diff = event.get_time() - self.last_start[2]
                # y el tiempo de click tiene que ser mayor a 250 milisegundos
                if dist_diff and time_diff > 250:
                    data = {"x": event.x, "y": event.y, "dx": dx, "dy": dy}
                    # Lanzo un click en la posicion del final del click
                    self.controlador.send_command("lanzar_click", data)
        else:
            # ignorar Gdk.EventType.TOUCH_UPDATE (multi-touch gestures!)
            return True

    def _cargar_ui_web(self, agregar=True):
        """
        Carga el browser, conecta el evento ``touch-event`` a lo inyecta en la ventana contenedora.

        Args:
            agregar (boolean): si True llama a :meth:`_agregar_browser <_agregar_browser>`.

        """
        uri = self._get_uri()
        self.browser = self.get_browser(uri)

        self.last_start = None
        self.browser.connect("touch-event", self._webkit2_touch)
        self.ventana.set_border_width(0)
        if agregar and self.browser is not None:
            self._agregar_browser()

    def _agregar_browser(self):
        """Agrega el browser a la ventana."""
        self.ventana.add(self.browser)

    def _descargar_ui_web(self):
        """Descarga la UI web."""
        if self.browser is not None:
            self.ventana.remove(self.browser)
            self.logger.info("Destruyendo ventana previa...")
            self.browser.destroy()

    def set_pantalla(self, pantalla):
        """Establece y muestra la pantalla en el panel principal del modulo.

        .. Caution:: Se usa solo durante los tests!!

        Arguments:
            pantalla ():
                La pantalla a mostrar. En realidad, se muestra el atributo panel de esta pantalla.
        """
        if (
            hasattr(self, "pantalla")
            and self.pantalla is not None
            and len(self.panel.get_children()) > 0
        ):
            self.panel.remove(self.pantalla)
            self.pantalla.destroy()
            self.pantalla = None

        self.pantalla = pantalla
        self.panel.add(self.pantalla)
        self.ventana.show_all()

    def main(self, titulo=None):
        """
        Ejecuta el modulo.

        Args:
            titulo (str): el título de la ventana.

        Returns:
            str: codigo de retorno. Siempre debe ser el nombre de un módulo o None
        """

        Gdk.threads_init()

        # Habilito el modo touchscreen, que desactiva el hover del cursor
        # settings = Gtk.Settings.get_default()
        # settings.set_property('gtk-long-press-time', 5000)

        self.loop = GObject.MainLoop()
        if titulo is not None:
            self.ventana.set_title(titulo)
        self.loop.run()
        return self.ret_code

    def quit(self, w=None):
        """
        Ejecuta Gtk.main_quit() y termina la ejecucion.

        .. Hint:: el parametro ``w`` no se usa en ningun lado.

        Args:
            w:

        Returns:
            boolean: siempre retorna False
        """
        if hasattr(self, "rampa") and self.rampa is not None:
            self.rampa.remover_consultar_lector()
            self.rampa.remover_consultar_tarjeta()
            self.rampa.desregistrar_eventos()

        if hasattr(self, "pantalla") and self.pantalla is not None:
            self.pantalla.destroy()
        if hasattr(self, "browser") and self.browser is not None:
            if hasattr(self, "ventana"):
                self.ventana.remove(self.browser)
            self.browser.destroy()
        if hasattr(self, "ventana"):
            self.ventana.destroy()
        if hasattr(self, "loop"):
            self.loop.quit()
        return False

    def admin(self):
        """Sale al modulo menu."""
        self.salir_a_modulo(MODULO_MENU)

    def salir_a_modulo(self, modulo):
        """Sale a un modulo.

        Arguments:
            modulo (str): el modulo al que sale.
        """
        self.logger.debug("Saliendo a modulo {}".format(modulo))
        self.ret_code = modulo
        self.quit()

    def show_dialogo(self, msg, btn_aceptar=False):
        """Mostrar un dialogo simple (localizado)"""
        msg = self.controlador.get_constants()["i18n"][msg]
        self.controlador.send_command(
            "cargar_dialogo_default", {"pregunta": msg, "btn_aceptar": btn_aceptar}
        )

    def hide_dialogo(self):
        """Esconde el dialogo."""
        self.controlador.hide_dialogo()

    def _start_audio(self):
        """Inicia el audioplayer."""
        global _audio_player
        if USAR_SONIDOS_UI and (_audio_player is None or not _audio_player.is_alive()):
            _audio_player = AudioPlayer()
            _audio_player.start()
        self._player = _audio_player

    def _stop_audio(self):
        """Para el audioplayer."""
        global _audio_player
        if _audio_player is not None:
            _audio_player.stop()

    def _play(self, nombre_sonido):
        """Ejecuta los audios de interacción con el usuario.

        Arguments:
            nombre_sonido (str): nombre del sonido a reproducir.
        """
        if USAR_SONIDOS_UI:
            self._start_audio()
            sonido = join(PATH_SONIDOS_VOTO, "{}.wav".format(nombre_sonido))
            self._player.play(sonido)

    def play_sonido_ok(self):
        """Ejecuta el sonido de "OK"."""
        self._play("ok")

    def play_sonido_warning(self):
        """Ejecuta el sonido de "Warning"."""
        self._play("warning")

    def play_sonido_error(self):
        """Ejecuta el sonido de "Error"."""
        self._play("error")

    def play_sonido_tecla(self):
        """Ejecuta el sonido de "Tecla presionada"."""
        self._play("tecla")

    def _load_config(self):
        """Carga las configuraciones para esta ubicación."""
        id_ubicacion = None
        if self.sesion.mesa is not None:
            id_ubicacion = self.sesion.mesa.codigo
        self._config = Config(self.config_files, id_ubicacion)

    def config(self, key):
        """Devuelve un valor de cofiguracion particular para esta ubicación.

        Arguments:
            key (str): la key de la cual queremos traer el valor.

        Returns:
            str: valor asociada a la clave.
        """
        value, file_ = self._config.data(key)
        self.logger.debug("Trayendo config {}: {} desde {}".format(key, value, file_))
        return value

    def en_disco(self, nombre_modulo):
        """Devuelve la existencia de un modulo.

        Arguments:
            nombre_modulo (str):
                el nombre del modulo que queremos averiguar si está en el disco actual.

        Returns:
            boolean: True si el módulo existe.
        """
        return exists(join(PATH_MODULOS, nombre_modulo))

    def get_brightness(self):
        """Devuelve el brillo de la pantalla."""
        if self.rampa.tiene_conexion:
            brightness = self.rampa.get_actual_brightness()
            if brightness is not None:
                self.controlador.brightness_level = int(brightness)

    @presencia_on_required
    def _recheck_plugged(self, data):
        """
        Hay conexión eléctrica:
        - Actualiza presencia
        """
        self.logger.warning("PLUGGED")
        self.presencia = True
        self.rampa.set_presencia_mode(False)
        self.controlador.ocultar_div_presencia()
        try:
            # Esto porque en los modulos donde no funciona presencia no va a existir el atributo
            # `self.controlador.brightness_level`. En un futuro, este dato debería migrar a la clase msa.modulos.Sesion
            self.controlador.set_specific_brightness(self.controlador.brightness_level)
        except Exception as e:
            pass
        self.start_presencia()
        self._reset_previuos_led_action()

    @presencia_on_required
    def _recheck_unplugged(self, data):
        """
        No hay conexión eléctrica:
        - Actualiza presencia
        """
        self.logger.warning("UNPLUGGED")
        self.rampa.set_presencia_mode(True)
        self.controlador.ocultar_div_presencia()
        self.start_presencia()

    @presencia_on_required
    def _cambio_presencia(self, data):
        """
        Cada vez que se detecte la presencia se encenderá la pantalla.
        Además, en caso se seteará el brillo en el valor que fue seteado
        por el usuario en mantenimiento.
        Cuando no se detecta presencia, el brillo bajará y empezará
        la espera de 5 segundos hasta apagar la pantalla.

        Args:
            data (bool): True, indicando al detección de presencia.
                False en caso de que sea por presencia no detectada
                durante x segundos.
        """
        self.logger.warning("cambio presencia")
        self.logger.warning("data: %s", bool(data["byte"]))
        if bool(data["byte"]):
            self.presencia = True
            self.controlador.set_specific_brightness(self.controlador.brightness_level)
            self.controlador.ocultar_div_presencia()
            self.controlador.encender_pantalla()
            self._reset_previuos_led_action()

        else:
            self.presencia = False
            self.controlador.set_specific_brightness(30)

            self.controlador.mostrar_div_presencia()
            self.atenuacion_checks = 0
            timeout_add(self.timer_timeout_ms, self._check_atenuacion)

    @presencia_on_required
    def _reset_previuos_led_action(self):
        if self.estado_leds is not None:
            self.rampa.set_led_action(self.estado_leds)
            self.estado_leds = None

    @presencia_on_required
    def _check_atenuacion(self):
        """
        Este método será utilizado dentro de un timer.
        Se esperarán X = int(self.atenuacion_ms / self.timer_timeout_ms) segundos (actualmente fijo en 5 segundos segun
        la instanciación de la clase) y al no detectar presencia se procederá con el apagado de la pantalla.
        Casos posibles:
            a. El modulo cambia estado `self.presencia` a `True`. En este caso, la funcion devuelve False y destruye el
            timer
            b. Pasaron los X segundos: apaga la pantalla y la funcion devuelve False y destruye el timer.
            c. Ninguno de los casos anteriores se da, el timer continua activo.
        """
        if self.presencia:
            return False
        self.atenuacion_checks += 1
        self.logger.info("Atenuacion checks: " + str(self.atenuacion_checks))
        if self.atenuacion_checks > int(self.atenuacion_ms / self.timer_timeout_ms):
            self.rampa.set_backlight_status(False)
            self.estado_leds = self.rampa.get_estado_leds()
            self.rampa.set_led_action("suspension")
            return False
        return True

    @presencia_on_required
    def start_presencia(self):
        """
        Verifica si hay conexión eléctrica y el estado de la presencia.
        En base a ello, procede a registrarse a los eventos necesarios
        o se desregistra
        """
        # registramos presencia cuando:
        # la máquina está enchufada
        # la presencia está activada desde mantenimiento
        # desregistramos presencia cuando:
        # la máquina está enchufada
        # la presencia está desactivada desde mantenimiento
        self.logger.warning("Start presencia " + self.nombre)
        self.logger.warning("activar_presencia " + str(self.activar_presencia))
        if self.activar_presencia:
            if self.rampa.tiene_conexion:
                power_source = self.rampa.get_power_source()
                if power_source in [None, False, True]:
                    power_source = self.rampa.get_power_source()
                power_source = not bool(power_source["byte"])
                self.logger.warning("obteniendo power source : %s", power_source)
                presencia_mode = bool(self.rampa.get_presencia_mode())
                self.logger.warning(
                    "obteniendo presencia mode ARMVE: %s", presencia_mode
                )
                if power_source:
                    self.logger.warning("maquina enchufada")
                    self.logger.warning("DESREGISTRO PRESENCIA")
                    self.rampa.remover_presence_changed()
                    # Resuelve problemas de inconsistencia: si recien se inicia el sistema,
                    # con la máquina enchufada y presencia activa por la setting, entonces
                    # el modo de presencia seguía siempre activo.
                    if presencia_mode:
                        self.rampa.set_presencia_mode(False)
                else:
                    if presencia_mode:
                        self.logger.warning("REGISTRANDO PRESENCIA")
                        self.rampa.registrar_presence_changed(self._cambio_presencia)
                    else:
                        self.logger.warning("presencia desactivada")
                        self.logger.warning("DESREGISTRO PRESENCIA")
                        self.rampa.remover_presence_changed()
                self.controlador.presence_reset(True)
        else:
            self.rampa.remover_presence_changed()
