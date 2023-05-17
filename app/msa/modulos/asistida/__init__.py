"""Modulo de votacion asistida.
Permite la votacion de personas con impedimentos visuales.

Hereda la mayoría de los comportamientos del modulo Sufragio.
"""
from gi.repository.GObject import idle_add

from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.core.data import Speech
from msa.modulos.asistida.controlador import Controlador
from msa.modulos.constants import E_VOTANDO, MODULO_SUFRAGIO
from msa.modulos.decorators import requiere_mesa_abierta
from msa.modulos.sufragio import Modulo as ModuloSufragio
from msa.core.exceptions import MesaIncorrecta
from msa.core.led_action.constants import PREVIOUS_LED_ACTION
import importlib

from gi.repository.GObject import timeout_add

class Modulo(ModuloSufragio):

    """Modulo para votacion asistida.
    Hereda del ModuloSufragio y agrega cosas específicas de la votación para
    personas con impedimentos visuales."""

    @requiere_mesa_abierta
    def __init__(self, *args, **kwargs):
        """Constructor. Inicializa lo mismo que Sufragio más el locutor."""
        ModuloSufragio.__init__(self, activar_presencia=False, *args, **kwargs)
        self.config_files = [COMMON_SETTINGS, MODULO_SUFRAGIO, self.nombre]
        self._load_config()
        self._start_audio()
        self.inicializar_locutor()

    def inicializar_locutor(self):
        """Inicializa el locutor, el cual es el proceso que habla en asistida."""
        if self.sesion.locutor is None:
            self.sesion.inicializar_locutor()
        if not self.sesion.locutor.is_alive():
            self.sesion.locutor.start()

    def _set_controller(self):
        """
        Se crea una instancia del Controlador.
        """
        nombre_controlador_asistida = self.config("controlador")
        Controlador = getattr(importlib.import_module("msa.modulos.asistida.controlador"), nombre_controlador_asistida)

        self.controlador = Controlador(self)

    def _inicio(self, *args, **kwargs):
        """Pisa el método inicio para mostrar el teclado."""
        ModuloSufragio._inicio(self, *args, **kwargs)
        if self.estado == E_VOTANDO:
            self.controlador.send_command("mostrar_teclado")

    def _error(self, cambiar_estado=True):
        """Lanza el error tanto en la interfaz visual como en la auditiva."""
        ModuloSufragio._error(self, cambiar_estado)

        def _locutar_error():
            """Ejecuta el sonido del error."""
            self.controlador.sesion.locutor.shutup()
            frases = [Speech.one("error_almacenado").texto,
                      Speech.one("error_almacenado_2").texto]
            self.sesion.locutor.decir(frases)
        idle_add(_locutar_error)


    def _consultar(self, tag):
        """
        Permite al elector consultar una boleta.
        En votacion asistida no permitimos verificar la boleta apoyandola.

        Args:
            tag (SoporteDigital): un objeto de clase SoporteDigital.
        """
        if self.rampa.tiene_papel:
            try:
                def _check_sin_papel():
                    if not self.rampa.tiene_papel:
                        self.sesion.locutor.shutup()
                        return False
                    return True

                self._mostrar_consulta(tag)
                timeout_add(300, _check_sin_papel)
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
