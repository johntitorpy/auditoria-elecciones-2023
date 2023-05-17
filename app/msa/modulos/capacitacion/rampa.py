"""Rampa del modulo capacitacion."""
from time import sleep, time

from msa.modulos.base.rampa import RampaBase, semaforo
from msa.modulos.constants import (E_CONSULTANDO, E_EN_CONFIGURACION,
                                   E_ESPERANDO, MODULO_CAPACITACION,
                                   E_REGISTRANDO)


class RampaCapacitacion(RampaBase):

    """La Rampa especializada para el modulo de capacitacion."""

    @semaforo
    def maestro(self):
        """
        Si se apoya un voto en el lector y el módulo no es capacitación, se consulta por el
        tag leído, caso contrario se expulsa la boleta.
        Si hay papel colocado en la máquina y el controlador es el de capacitación
        verifica que el estado del mismo sea
        :const:`E_EN_CONFIGURACION <modulos.constants.E_EN_CONFIGURACION>`, caso contrario expulsa
        la boleta.
        Si el estado era ``E_EN_CONFIGURACION`` entonces verifica que el tag sea vacío y manda a
        imprimir la boleta utilizando el controlador que se encuentra seteado.
        """
        # si apoyan un voto
        if self.tag_leido is not None and self.tag_leido.es_voto():
            # si no estamos en el menu
            if self.modulo.web_template != "capacitacion":
                self.modulo._consultar(self.tag_leido)
            else:
                self.expulsar_boleta()
        # si hay papel puesto
        elif self.tiene_papel:
            controlador = self.modulo.controlador
            # Si el controlador es el de capacitacion y no el de sufagio
            if controlador.nombre == MODULO_CAPACITACION:
                # para cuando queremos imprimir un tag desde el menu
                if controlador.estado == E_EN_CONFIGURACION and self.modulo.estado != E_REGISTRANDO:
                    if(self.tag_leido is not None and
                       self.tag_leido.es_tag_vacio()):
                        sleep(1)
                        controlador.hide_dialogo()
                        self.modulo.imprimir_boleta()
                    else:
                        self.set_led_action('reset')
                        controlador.error_boleta_no_vacia()
                        self.expulsar_boleta()
                else:
                    self.expulsar_boleta()
            # si meto un tag vacio en el con el controlador de sufagio y estoy
            # haciendo tiempo como si estuviera imprimiendo el voto
            elif self.modulo.estado != E_REGISTRANDO:
                self.modulo.hay_tag_vacio()
        # si no estamos en ningun estaddo de votacion vamos a mostar la
        # pantalla de insercion
        elif self.modulo.estado not in (E_CONSULTANDO, E_ESPERANDO):
            self.modulo.pantalla_insercion()

    def tag_admin(self, tag=None):
        """Metodo que se llama cuando se apoya un tag de admin."""
        if tag is not None and (tag.es_capacitacion() or tag.es_autoridad()) and self.modulo.time_last_tag is None:
            self.modulo.time_last_tag = time()
            
    def no_tag(self, tag=None):
        current = time()
        if self.modulo.time_last_tag is not None and current - self.modulo.time_last_tag > 3:
            self.modulo.time_last_tag = None
            self.modulo._calibrar_pantalla()
        elif self.modulo.time_last_tag is not None:
            self.modulo.time_last_tag = None
            self.modulo.salir()

    def registrar_voto(self, seleccion, solo_imprimir, aes_key, callback):
        """
        Registra un voto en una BUE (Boleta Única Electrónica)

        Args:
            seleccion (dict): Contiene la selección de los candidatos.
            imprimir (bool): Indica si se desea imprimir y no grabar en el tag.
            aes_key (bytes): Clave con la cual se encriptan los votos.
            callback (function): Callback que se llama al finalizar el registro.

        Returns:

        """
        respuesta = self._servicio.registrar_voto(seleccion, solo_imprimir,
                                                  aes_key, callback)
        return respuesta
