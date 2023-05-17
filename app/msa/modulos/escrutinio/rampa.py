"""Rampa del modulo escrutinio."""

from gi.repository.GObject import timeout_add

from msa.core.rfid.constants import TAG_COLISION
from msa.modulos.base.rampa import RampaBase
from msa.modulos.constants import E_IMPRIMIENDO, E_RECUENTO

class Rampa(RampaBase):

    """
    Rampa que maneja las particularidades del modulo de recuento que es el mas
    complejo en cuanto a estados.
    """

    def maestro(self):
        if self.modulo.estado != E_IMPRIMIENDO:
            # esperar una fracción de segundo para forzar leer y actualizar UI:
            def _reevaluar():
                # si sigo teniendo papel puesto
                if self.tiene_papel and self.tag_leido is None:
                    # Le pido al service el contenido del tag
                    self.tag_leido = self.get_tag()
                    if self.tag_leido is None:
                        # si no hay tag, reinicio preventivamente el ARMVE
                        self.sesion.logger.debug("Sin TAG leido, reiniciando")
                        self.reset_rfid()
            if not self.tag_leido or True:
                timeout_add(200, _reevaluar)
            timeout_add(3000, self.expulsar_boleta, "recuento")

    def cambio_tag(self, tipo_lectura, tag):
        """ Callback de cambio de tag.

        Args:
            tipo_lectura (str): Tipo de tag.
            tag (str): Representación de los tados del tag.

        """
        # guardar último tag para detectar su presencia:
        if tag != self.tag_leido:
            self.tag_leido = tag
        # solo proceso si es un evento de cambio de tag
        if tag is not None:
            if None not in (tag.serial, tag.tipo, tag.datos):
                if tag.es_voto():
                    self.modulo.procesar_voto(tag)
                elif tag.es_autoridad():
                    self.modulo.preguntar_salida()
                else:
                    # no es un voto
                    # ante un cambio de tag:
                    # si el estado es Recuento entonces se encienden leds ante error
                    # si el estado no es Recuento (por ejemplo cuando se imprimen actas),
                    # entonces no enciende led de error ante cambio de tag.
                    encender_led = False if self.modulo.estado != E_RECUENTO else True
                    self.modulo.error_lectura(encender_led=encender_led)
            elif tipo_lectura == TAG_COLISION:
                self.modulo.error_lectura()
