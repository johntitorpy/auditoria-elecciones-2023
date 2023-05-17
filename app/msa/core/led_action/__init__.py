from time import sleep

from msa.core.armve.protocol import Leds
from msa.core.led_action.constants import (
    FIXED, BLINK, ACTIONS, LED_PERIOD,
    PREVIOUS_LED_ACTION, SEESAW_SPEED,
    BLINK_TWO_COLORS
)
from msa.core.led_action.helpers import Dummy
from msa.core.logging import get_logger

logger = get_logger("led_action")


class LedAction():

    """Maneja el comportamiento de los leds segun las acciones que se envían
    desde el módulo"""

    def __init__(self, buffer):
        self.leds = Leds(buffer)
        self.reset()
        self.estado = None

    def __new__(cls, buffer):
        """Se utiliza esta función para la compatibilidad P4/P6, ya que los
        leds sólo están implementados en P6. Para no tener errores en P4,
        cuando se instancia la clase se devuelve otra clase Dummy que no hace
        nada cuando se ejecutan los métodos
        """
        if buffer is None:
            logger.info('Se instancia una clase dummy porque P4 no tiene leds')
            return Dummy()
        return super(LedAction, cls).__new__(cls)

    def set_action(self, action, next_action=None):
        """ Busca en la parametrización la acción y la ejecuta"""
        logger.info('Acción de led: {}'.format(action))
        logger.info('Acción anterior de led: {}'.format(self.estado))
        logger.info('Acción siguiente de led: {}'.format(next_action))
        # apago todos los leds
        self.reset()
        # controlo si tengo que volver a la acción anterior
        if action == PREVIOUS_LED_ACTION:
            action = self.estado
        # me fijo si está parametrizada la acción
        if action in ACTIONS:
            # la parametrización contiene: led - color - behavior - timeout
            for led in ACTIONS[action]:
                # llamo al a funcion que corresponda en base al comportamiento
                if led['behavior'] == FIXED:
                    self._set_color(
                        led['id_led'], led['color'], led['timeout']
                    )
                elif led['behavior'] == BLINK:
                    self._blink_color(
                        led['id_led'], led['color'], led['timeout']
                    )
                elif led['behavior'] == BLINK_TWO_COLORS:
                    self._blink_two_colors(
                        led['id_led'], led['color'], led['color2'], led['timeout']
                    )
                else:
                    self._seesaw_color(
                        led['id_led'], led['color'], led['timeout']
                    )
            # si no hay acción siguiente, lo guardo como la actual
            if next_action is None:
                self.estado = action
        logger.info('Acción que queda: {}'.format(self.estado))
        return action

    def get_estado_leds(self):
        return self.estado

    def _set_color(self, id_led, color, timeout):
        """Setea el color del led fijo"""
        self.leds.set_color(id_led, color, timeout, 1)

    def _blink_color(self, id_led, color, timeout):
        """Setea el color del led blinkeando"""
        self.leds.blink_color(id_led, color, LED_PERIOD, timeout, 1)

    def _blink_two_colors(self, id_led, color, color2, timeout):
        """Setea el color del led blinkeando"""
        self.leds.blink_two_colors(id_led, color, color2, LED_PERIOD, timeout, 1)

    def _seesaw_color(self, id_led, color, timeout):
        """Setea el color del led pulsando"""
        self.leds.seesaw_color(id_led, color, SEESAW_SPEED, timeout, 1)

    def reset(self):
        """Apaga todos los leds"""
        self._set_color(
            ACTIONS['reset'][0]['id_led'], ACTIONS['reset'][0]['color'], 0
        )
