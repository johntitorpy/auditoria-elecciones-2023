"""Rampa del modulo mantenimiento."""
from msa.modulos import get_sesion
from msa.modulos.base.rampa import RampaBase, semaforo


sesion = get_sesion()


class Rampa(RampaBase):

    """La Rampa especializada para el modulo de administracion."""

    @semaforo
    def maestro(self):
        """El maestro de ceremonias, el que dice que se hace y que no."""
        pass

    def registrar_eventos(self):
        """Registra los eventos por default de la rampa."""
        if self.tiene_conexion:
            self.registrar_default_lector()
            self.registrar_default_sensor_1()
            self.registrar_default_sensor_2()

            modulo = self.modulo

            self.registrar_ac(modulo._recheck_batteries)
            self.registrar_ac(modulo._recheck_plugged)
            self.registrar_battery_discharging(modulo._recheck_batteries)
            self.registrar_battery_discharging(modulo._recheck_unplugged)
            self.registrar_presence_changed(modulo._cambio_presencia)
            
    def desregistrar_eventos(self):
        """desegistra los eventos por default de la rampa."""
        self.remover_consultar_lector()
        self.remover_insertando_papel()
        self.remover_nuevo_papel()

        if self.tiene_conexion:
            self.remover_ac()
            self.remover_battery_discharging()
            self.remover_battery_plugged()
            self.remover_battery_unplugged()
            self.remover_pir_detected()
            self.remover_pir_not_detected()
            self.remover_presence_changed()

    def cambio_tag(self, tipo_lectura, tag):
        """ Callback de cambio de tag.

        Argumentos:
            tipo_lectura -- el tipo de lectura del tag
            tag -- los datos del tag
        """
        self.modulo.rfid_check(tag)
    
