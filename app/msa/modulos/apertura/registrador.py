from base64 import b64encode

from msa.core.rfid.constants import TAG_APERTURA
from msa.modulos.constants import E_REGISTRANDO, E_INICIAL
from msa.modulos.apertura.constants import CANTIDAD_APERTURAS
from msa.settings import QUEMA


class RegistradorApertura:

    """Clase para el manejo de la impresion de las actas de apertura.

    Attributes:
        modulo (modulos.base.modulo.ModuloBase): se usa para interactuar con la vista del modulo de apertura
        Apertura (Apertura): se usa para interactuar con la vista del modulo de apertura
        actas_impresas (int): indica la cantidad de actas que se han imprimido.
    """

    def __init__(self, modulo):
        self.modulo = modulo
        self.rampa = modulo.rampa
        self.logger = modulo.sesion.logger

        self.actas_impresas = 0

    def registrar(self, apertura):
        """
        Registra una (o más) Apertura.

        El modulo Apertura tiene la particularidad de ser el único modo que
        levanta con un papel puesto, por lo tanto no estamos 100% seguros a
        alto nivel de que efectivamente el papel esté puesto (podemos tener
        falsos negativos), por lo tanto hacemos se consulta el estado del papel.

        Args:
            apertura (Apertura): es el template de la apertura que se quiere imprimir.
        """
        self.logger.info("registrando")
        self.modulo.estado = E_REGISTRANDO
        self.rampa.remover_nuevo_papel()

        self._datos = apertura.a_tag()
        # El modulo Apertura tiene la particularidad de ser el unico modo que
        # levanta con un papel puesto, por lo tanto no estamos 100% seguros a
        # alto nivel de que efectivamente el papel esté puesto (podemos tener
        # falsos negativos), por lo tanto hacemos este shortcut para
        # preguntarlo explicitamente al backend.
        tiene_papel = self.rampa._servicio._estado_papel()

        if not tiene_papel or self.rampa.tag_leido is None:
            self.logger.error("No tengo papel")
            self._error()
        else:
            self._guardar_tag(apertura)

    def _error(self):
        """
        Maneja un error al intentar registrar un acta.
        """
        self.rampa.remover_boleta_expulsada()
        self.modulo.controlador.msg_error_apertura(self.rampa.tag_leido)
        self.rampa.expulsar_boleta()
        self.rampa.registrar_nuevo_papel(self._reintentar)

    def _reintentar(self, *args):
        """
        Reintenta imprimir un acta.
        """
        self.rampa.tiene_papel = True
        self.modulo.hide_dialogo()
        self.modulo.reimprimir()

    def _guardar_tag(self, apertura):
        """
        Guarda un tag de una Apertura.

        Args:
            apertura (Apertura): Template de Apertura que se quiere guardar.
        """
        self.logger.debug("guardando_tag")
        # limitar datos a guardar en el chip (ej. excluir nombre autoridades)
        self.rampa.guardar_tag_async(self._tag_guardado, TAG_APERTURA,
                                     apertura.a_tag(compacto=True), QUEMA)

    def _tag_guardado(self, exito):
        """
        Callback que se ejecuta luego de intentar guardar un tag.

        Args:
            exito (bool): Indica si el tag se guardó exitosamente. En
                caso de que sea ``False`` se lanza un error y se resetea
                el RFID. En caso de que sae ``True``, se procede a
                imprimir.
        """
        if not exito:
            self.logger.error("El tag NO se guardó correctamente.")
            # Por las dudas reseteamos el RFID
            self.rampa.reset_rfid()
            self._error()
        else:
            self.logger.info("El tag se guardó correctamente.")
            self._imprimir()

    def _imprimir(self):
        """
        Imprime una Apertura.
        Contiene los pasos necesarios para enviar la orden
        de impresión.
        """
        self.logger.info("Imprimiendo acta de Apertura.")
        self.rampa.registrar_boleta_expulsada(self._fin_impresion)
        self.rampa.registrar_error_impresion(self._error)
        self.modulo.rampa.imprimir_serializado("Apertura",
                                               b64encode(self._datos))

    def _fin_impresion(self, *args):
        """
        Callback que se llama una vez que se terminó de imprimir un acta.
        Se verifica la cantida de actas impresas. En el caso de que
        dicha cantidad sea igual a la constante ``CANTIDAD_APERTURAS``,
        se llama al callback que nos permite salir. Caso contrario, se
        pasa el estado del módulo a ``INICIAL`` y se llama al callback que
        pide papel.
        """

        self.logger.debug("Fin de la impresion del acta.")
        self.rampa.remover_boleta_expulsada()

        self.actas_impresas += 1
        if self.actas_impresas == CANTIDAD_APERTURAS:
            self.logger.debug("Saliendo.")
            self.modulo.callback_salir()
        else:
            self.logger.debug("Pidiendo otra acta.")
            self.modulo.estado = E_INICIAL
            self.modulo.callback_proxima_acta()
            self.rampa.registrar_nuevo_papel(self.modulo.reimprimir)

