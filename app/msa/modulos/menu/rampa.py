"""Rampa del modulo Menu."""
from msa.core.armve.constants import DEV_PRINTER
from msa.modulos.base.rampa import RampaBase, semaforo
from msa.modulos.constants import MODULO_INICIO
from msa.core.led_action.constants import PREVIOUS_LED_ACTION

class Rampa(RampaBase):

    """La Rampa especializada para el modulo de administracion."""

    def registrar_eventos(self):
        RampaBase.registrar_eventos(self)
        self.registrar_reset_device(self._device_reset)

    def desregistrar_eventos(self):
        self.remover_reset_device()
        RampaBase.desregistrar_eventos(self)

    def _device_reset(self, device):
        if device == DEV_PRINTER:
            self.modulo.salir_a_modulo(MODULO_INICIO)

    @semaforo
    def maestro(self):
        """El maestro de ceremonias, el que dice que se hace y que no."""
        if self.tiene_papel:
            self.set_led_action('error_boleta_a_expulsar', PREVIOUS_LED_ACTION)
            self.expulsar_boleta()

    def cambio_tag(self, tipo_lectura, tag):
        """ Callback de cambio de tag.

        Argumentos:
            tipo_lectura -- el tipo de tag
            tag -- un objeto de clase SoporteDigital
        """
        if self.tiene_papel:
            self.expulsar_boleta()

        if tag is not None:
            controlador =  self.modulo.controlador
            # si pusieron un tag de autoridad
            if tag.es_autoridad():
                self.set_led_action('error_lectura_antena')
                controlador.mostrar_botonera()
            elif tag.es_tecnico() and controlador.timer is not None:
                # IMPORTANTE: habilitado sólo si la pantalla no está bloqueada
                # si el tag es de tecnico vamos a mostrar el boton de
                # mantenimiento la primera vez que lo pongan, la segunda vamos
                # a calibrar la pantalla.
                if self.modulo.boton_mantenimiento:
                    self.modulo._calibrar_pantalla()
                else:
                    controlador.reiniciar_timer()
                    self.set_led_action('ok_lectura_antena')
                    self.modulo.mostrar_boton_mantenimiento()
    
