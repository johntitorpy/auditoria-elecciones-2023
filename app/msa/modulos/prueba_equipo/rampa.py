"""Rampa del modulo sufragio."""
from gi.repository.GObject import timeout_add
from base64 import b64decode
from msa.modulos import get_sesion
from msa.core.documentos.boletas import PruebaEquipo
from msa.modulos.base.rampa import RampaBase, semaforo
from msa.modulos.prueba_equipo.constants import (
    E_GRABANDO_TAG,
    E_IMPRIMIENDO,
    E_VERIFICACION_TAG,
    E_IMPRESION_FINALIZADA,
    E_BOLETA_QUEMADA,
    E_VERIFICACION_IMAGEN,
    E_VALIDADO,
    E_ESPERANDO_BOLETA,
    E_POPUP,
    E_ERROR_VERIFICACION_TAG,
    E_ERROR_GRABAR_CHIP,
    E_ERROR_IMPRESION,
)

from msa.core.rfid.constants import TAG_PRUEBA_EQUIPO

from time import sleep


from msa.core.logging import get_logger

logger = get_logger("prueba_equipo")


class Rampa(RampaBase):

    """La Rampa especializada para el modulo de votacion."""

    @semaforo
    def maestro(self):
        """El maestro de ceremonias, el que dice que se hace y que no."""

        logger.info("INICIA RAMPA")
        logger.info(
            "Tiene papel: "
            + str(self.tiene_papel)
            + ", tag_leido: "
            + str(self.tag_leido)
        )
        logger.info("ESTADO " + str(self.modulo.estado))

        if self.modulo.estado == E_ESPERANDO_BOLETA:
            if self.tiene_papel:
                self.tag_generado = None
                if self.tag_leido is not None:
                    if self.tag_leido.es_tag_vacio():
                        logger.info("CASO 1")
                        self.pantalla_boleta_grabando_chip()
                    else:
                        logger.info("CASO 2")
                        self.modulo.tag_grabado()
                        self.expulsar_boleta("Tag grabado")

                elif self.tag_leido is None:
                    logger.info("CASO 3")

                    # reiniciar el RFID e Impresora preventivo
                    self.sesion.logger.warning("Hay papel sin tag leido...")
                    if self.modulo.estado != E_GRABANDO_TAG:
                        self.reset_rfid()

                    def _reevaluar():
                        # si sigo teniendo papel puesto (ignorar si está imprimiendo)
                        if self.tiene_papel and self.modulo.estado != E_GRABANDO_TAG:
                            logger.info("CASO 3.1")
                            # Le pido al service el contenido del tag
                            self.tag_leido = self.get_tag()
                            if self.tag_leido is None:
                                # si el tag no tiene datos muestro la pantalla de
                                # inicio y expulso la boleta
                                logger.info("CASO 3.1.1")
                                timeout_add(
                                    1000,
                                    self.expulsar_boleta,
                                    "Reevaluar - Hay papel sin tag",
                                )
                            else:
                                logger.info("CASO 3.1.2")
                                # en caso contrario llamo de nuevo a la logica que
                                # evalúa que hacer con la boleta que estan metiendo
                                self.maestro()

                    # espero cierto tiempo para volver a evaluar, ya que quizas el
                    # papel está aun entrando.
                    timeout_add(200, _reevaluar)

            else:
                logger.info("CASO 4")

        elif self.modulo.estado == E_VERIFICACION_TAG:

            if self.tag_leido != None:
                logger.info("CASO 6")
                self._evaluar_tag_leido()

            elif self.tiene_papel:

                logger.info("CASO 6.2")

                def _reevaluar():
                    # si sigo teniendo papel puesto (ignorar si está imprimiendo)
                    if self.tiene_papel and self.modulo.estado == E_VERIFICACION_TAG:
                        logger.info("CASO 6.2.1")
                        # self.tag_leido = self.get_tag()
                        if self.tag_leido is None:
                            logger.info("CASO 6.2.1.1")
                            timeout_add(
                                1000,
                                self.expulsar_boleta,
                                "Reevaluar - Hay papel sin tag",
                            )
                        else:
                            logger.info("CASO 6.2.1.2")
                            self.maestro()

                timeout_add(200, _reevaluar)

        elif self.modulo.estado in (
            E_IMPRESION_FINALIZADA,
            E_VERIFICACION_IMAGEN,
            E_VALIDADO,
            E_POPUP,
            E_ERROR_VERIFICACION_TAG,
            E_ERROR_GRABAR_CHIP,
            E_IMPRIMIENDO,
            E_ERROR_IMPRESION,
            E_BOLETA_QUEMADA,
        ):
            logger.info("CASO 7")
            if self.tiene_papel:
                self.expulsar_boleta(
                    "Estado " + self.modulo.estado + " no necesita boleta en rampa."
                )

    def cambio_tag(self, tipo_lectura, tag):
        """Callback de cambio de tag.

        Argumentos:
            tipo_lectura -- el tipo de tag
            tag -- la representacion de los tados del tag

        """

        logger.info("CAMBIO_TAG")
        self.tag_leido = tag
        self.maestro()

    def _evaluar_tag_leido(self):
        tag_leido = self.tag_leido.a_dict()
        print(tag_leido["tipo"])
        tag_leido_b64 = b64decode(tag_leido["datos"])
        print(self.tag_generado)
        print(tag_leido_b64)

        if (self.tag_generado == tag_leido_b64) and (
            tag_leido["tipo"] == TAG_PRUEBA_EQUIPO
        ):
            logger.info("CASO 6.1")
            if self.modulo.estado != E_VALIDADO:
                logger.info("CASO 6.2")
                self.desregistrar_lector()
                self.desregistrar_evento_papel()
                self.modulo.pantalla_validacion()
        else:
            logger.info("CASO 6.3")
            self.modulo.pantalla_error_lectura_chip()
            if self.tiene_papel:
                timeout_add(
                    1000,
                    self.expulsar_boleta,
                    "Boleta - Tag grabado no es Prueba de Equipo",
                )

    def pantalla_boleta_grabando_chip(self):
        pruebaEquipo = PruebaEquipo()
        self.tag_generado = pruebaEquipo.a_tag(10)
        self.modulo.boleta_grabando_chip()
        timeout_add(200, self._grabar_tag_prueba_equipos)

    def _grabar_tag_prueba_equipos(self):
        self._servicio.guardar_tag_async(
            self._tag_guardado, TAG_PRUEBA_EQUIPO, self.tag_generado, True
        )

    def registrar_voto(self, seleccion, solo_imprimir, aes_key, callback):
        respuesta = self._servicio.registrar_voto(
            seleccion, solo_imprimir, aes_key, callback
        )
        return respuesta

    def _tag_guardado(self, exito):
        """Callback que se ejecuta luego de intentar guardar un tag.

        Argumentos:
            exito -- un booleano que indica si el tag se guardó exitosamente.
        """
        if exito:
            self.modulo.tag_grabado_correctamente()
        else:
            self.modulo.tag_error_grabar()

        timeout_add(500, self._imprimir_boleta)

    def _imprimir_boleta(self):
        self.tiene_papel = self._servicio._estado_papel()
        if self.tiene_papel:
            self.registrar_fin_impresion(self._fin_impresion)
            self.modulo.rampa.registrar_error_impresion(self._error_impresion)
            self.modulo.imprimir_boleta()
        else:
            self._error_impresion()

    def pantalla_impresion_confirmada(self):
        self.modulo.boleta_impresa_correctamente()

    def _error_impresion(self):
        self.remover_boleta_expulsada()
        self.modulo.error_boleta_impresion()
        timeout_add(1000, self.expulsar_boleta, "error impresion")

    def _fin_impresion(self):
        """Callback que se llama una vez que se terminó de imprimir un acta."""
        logger.warning("_FIN_IMPRESION")
        self.tiene_papel = self._servicio._estado_papel()
        self.remover_boleta_expulsada()
        self.pantalla_impresion_confirmada()

    def imprimir_serializado(
        self, tipo_tag, tag, transpose=False, only_buffer=False, extra_data=None
    ):
        self._servicio.imprimir_serializado(
            tipo_tag,
            tag,
            transpose=transpose,
            only_buffer=only_buffer,
            extra_data=extra_data,
        )

    def desregistrar_lector(self):
        """desregistra los eventos por default del lector."""
        self.remover_consultar_lector()

    def desregistrar_evento_papel(self):
        """desregistra los eventos por default del papel de la rampa."""
        self.remover_insertando_papel()
        self.remover_nuevo_papel()

    def registrar_lector(self):
        """Registra los eventos por default del lector."""
        self.registrar_default_lector()
