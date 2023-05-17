"""
    Rampas para el modulo ingreso de datos.
"""

from msa.core.rfid.constants import TAG_ADMIN
from msa.modulos.base.rampa import RampaActas


class RampaCopiasCertificado(RampaActas):

    """
    Rampa que maneja las particularidades del modulo de recuento que es el mas
    complejo en cuanto a estados.
    """

    def cambio_sensor_1(self, data):
        """Callback que se corre cuando el sensor 1 se dispara.

        El evento que nos interesa es el que manda False en el sensor_1
        ya que nos dice que el papel ya esta listo para leer el chip.
        """
        self.expulsar_boleta()

    def cambio_sensor_2(self, data):
        """Callback que se corre cuando el sensor 2 se dispara.

        El evento que nos interesa es el que manda "0" en ambos sensores ya que
        nos dice que el papel ya esta listo para leer el chip.
        """
        self.expulsar_boleta()

    def cambio_tag(self, tipo_lectura, tag):
        """ Callback de cambio de tag.

        Argumentos:
            tipo_lectura -- el tipo de tag
            tag -- los datos del tag
        """
        if tag is not None:
            if tipo_lectura == TAG_ADMIN:
                self.modulo.salir()
            elif tag.es_recuento():
                self.modulo.cargar_recuento_copias(tag)

    def procesar_tag(self, tag):
        pass
