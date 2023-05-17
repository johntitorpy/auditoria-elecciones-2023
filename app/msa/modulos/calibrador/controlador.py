"""Controlador y Actions del módulo calibrador."""
from random import randint


from msa.core.i18n import levantar_locales
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.calibrador.settings import (
    TH_DUALCLICK, TH_ERRORES, TH_MISCLICK)
from msa.modulos.gui.settings import MOSTRAR_CURSOR

levantar_locales()

from msa.core.logging import get_logger

logger = get_logger("calibrador")

class Actions(BaseActionController):
    """Acciones para el controlador del calibrador."""

    def initiate(self, data):
        self.controlador.initiate(data)

    def calibrar(self, datos_calibracion):
        logger.info(datos_calibracion)
        self.controlador.modulo.calibrar(datos_calibracion)
        self.controlador.verificar_calibracion()

    def reiniciar(self, data):
        self.controlador.modulo.reiniciar()

    def terminar(self, data):
        self.controlador.modulo.quit()


class Controlador(ControladorBase):

    """Controlador para la interfaz web del calibrador."""

    def __init__(self, modulo):
        ControladorBase.__init__(self, modulo)
        self.add_processor("calibrador", Actions(self))

        self.calibrador = modulo.calibrador

    def crear_orden(self):
        """
        Define un orden aleatorio a los puntos.
        Returns
            list: Lista de puntos ordenados aleatoriamente.
        """
        def rotar_lista(l, x):
            return l[-x:] + l[:-x]

        puntos = ['tl', 'bl', 'br', 'tr']
        puntos = rotar_lista(puntos, randint(0, 3))
        if randint(0, 1) == 1:
            puntos = puntos[::-1]

        return puntos

    def inicializar(self, data):
        """
        Genera un diccionario de datos por default. El diccionario tiene las claves ``th_adyayente``,
        ``th_duplicado``, ``th_errores``, ``mostrar_cursor``, ``locale``, ``punto_verificacion``,
        ``orden`` y ``posiciones``.

        Luego ejecuta la función del front-end ``ready`` enviando el diccionario creado.

        """
        data = {
            'th_adyacente': TH_MISCLICK,
            'th_duplicado': TH_DUALCLICK,
            'th_errores': TH_ERRORES,
            'mostrar_cursor': MOSTRAR_CURSOR,
            'locale': self.get_base_data(),
            'punto_verificacion': self.modulo.obtener_punto_verficacion(),
            'orden': self.crear_orden(),
            'posiciones': self.calibrador.puntos_calculados
        }
        self.send_command('calibrador_ready', data)

    def verificar_calibracion(self):
        """Ejecuta la función del front-end ``verificar_calibracion``."""
        self.send_command('verificar_calibracion')

    def reiniciar(self, punto_verificacion):
        """
        Genera un diccionario con datos necesarios para reiniciar el calibrador. Dicho
        diccionario tiene ``punto_verificacion`` y ``orden`` como claves.

        Luego ejecuta la función del front-end ``reiniciar``, enviando el diccionario creado.
        """
        datos = {
            'punto_verificacion': punto_verificacion,
            'orden': self.crear_orden()
        }
        self.send_command('reiniciar', datos)

    def terminar(self, data=None):
        """Sale del módulo."""
        self.modulo.quit()

    def get_base_data(self):
        """
        Genera un diccionario que contiene como claves cada texto que aparece en la pantalla
        del calibrador y como valor el texto mismo. Entre las claves de este diccionario se
        encuentran: ``titulo``, ``msj_inicio_calibracion``, ``msj_calibrando``,
        ``msj_sig_punto``, ``msj_fin_calibracion``, ``msj_reinicio_calibracion_error``,
        ``msj_reinicio_calibracion_verif``, ``error_misclick``, ``error_doubleclick`` y
        ``error_time``.

        Returns:
           dict: Diccionario de datos.
        """
        data = {
            'titulo': _('calibrador_titulo'),
            'msj_inicio_calibracion': 'Para comenzar a calibrar la pantalla mantenga presionado el botón azul',
            'msj_calibrando': 'Por favor, mantenga presionado el botón azul hasta que cambie de posición',
            'msj_sig_punto': 'Continue el proceso con el siguiente punto',
            'msj_fin_calibracion': 'Para verificar la calibración mantenga presionado el botón azul',
            'msj_reinicio_calibracion_error': 'Por la ocurrencia de errores sucesivos se reinició el proceso de calibración',
            'msj_reinicio_calibracion_verif': 'Se reinició el proceso de calibración porque se detectó que la calibración no fue exitosa',
            'error_misclick': _('calibrador_error_misclick'),
            'error_doubleclick': _('calibrador_error_dobleclick'),
            'error_time': _('calibrador_error_tiempo')
        }

        return data
