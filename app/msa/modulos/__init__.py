"""
Los modulos que componen al sistema.

Cada modulo es independiente, pero todos pueden heredar de :meth:`modulos.base.modulo.ModuloBase` para
facilitar la implementacion y mantenimiento.

Cada modulo debe tener un método ``main()``, que puede o no devolver un
string. Si el valor de este string es uno de los módulos habilitados en
:attr:`modulos.base.App.modulos_habilitados <modulos.base.App.modulos_habilitados>` se ejecutará ese modulo.


.. todo::
    :meth:`ModuloBase` debería tener una relacion de asociación con el controlador y no esperar que alguna clase
    hija la tenga.

.. todo::
    Hay muchos métodos que sólo ejecutan una línea y solo se usan una vez. Esa línea de codigo podría ser ejecutada
    desde el lugar donde se la llama.

"""

from ojota import current_data_code

from msa.core.audio.speech import Locutor
from msa.core.logging import get_logger
from msa.core.ipc.client import IPCClient
from msa.settings import MODO_DEMO


_sesion_actual = None
"""Guarda la instancia de la sesion actual"""


class Sesion(object):

    """
    Clase que maneja informacion de sesion de voto.

    Attributes:
        _mesa (core.data.Ubicacion): Mesa de la sesion.
        apertura (core.documentos.actas.Apertura): Se usa para establecer el acta de apertura durante esta sesion.
        _tmp_apertura (core.documentos.actas.Apertura):
            Acta de apertura temporal, se usa hasta que se registra esta como la
            :meth:`apertura <~Sesion.apertura>` definitiva.
        recuento (core.documentos.actas.Recuento): Se usa para almacenar el recuento durante esta sesion.
        credencial (core.documentos.soporte_digital.SoporteDigital):
            Guarda el tag de la credencial. Solo puede ser un tag tipo
            :const:`TAGS_ADMIN <core.rfid.constants.TAGS_ADMIN>`
        locutor (core.audio.speech.Locutor): Se encarga de reproducir los audios para asistida.
        modo_demo (bool): establece si es modo demo segun :const:`settings.MODO_DEMO`.
        logger (logging.Logger): obtiene un Logger con :meth:`get_logger <core.logging.get_logger>`
        _servicio (core.ipc.client.IPCClient): cliente IPC.
    """

    def __init__(self, iniciar_hw=True):
        """
        Obtiene el Logger, establece todos los atributos en None excepto :meth:`modo_demo <~modo_demo>` y finalmente, si
        el parametro ``iniciar_hw`` es True, llama a :meth:`~Sesion._init_hardware`.

        Arguments:
            iniciar_hw (bool):
                Indica si se debe iniciar el hardware o no.
        """
        self.logger = get_logger("modulos")

        self.retornar_a_modulo = None
        self._mesa = None
        self.apertura = None
        self.recuento = None
        self.credencial = None
        self._tmp_apertura = None
        self.locutor = None
        self.modo_demo = MODO_DEMO

        # interaccion con hardware
        if iniciar_hw:
            self._init_hardware()
        else:
            self._servicio = None

    def _init_hardware(self):
        """
        Instancia el atributo ``_servicio`` con un :meth:`IPCClient <core.ipc.client.IPCClient>`
        """
        self._servicio = IPCClient(self)

    def getmesa(self):
        """
        Devuelve la mesa de la sesion.

        Returns:
            core.data.Ubicacion: la mesa.

        """
        return self._mesa

    def setmesa(self, value):
        """
        Establece la mesa en la sesion.

        Args:
            value (core.data.Ubicacion): la mesa

        """
        self._mesa = value

        if self._mesa is not None:
            self._mesa.usar_cod_datos()
        else:
            current_data_code(None)

    mesa = property(getmesa, setmesa)

    def inicializar_locutor(self):
        """
        Crea una instancia de :meth:`Locutor <core.audio.speech.Locutor>` y se la asigna al atributo
        :attr:`~Sesion.locutor`
        """
        self.locutor = Locutor()


def get_sesion(iniciar_hw=True, force=False):
    """
        Obtiene la sesion actual. Si no existe una, la crea y la almacena en la variable global ``_sesion_actual``

        .. todo::
            Mal implementado. La clase :meth:`Sesion <modulos.Sesion>` debería ser singleton y así se puede manejar
            correctamente una sola instancia en el sistema.

        Args:
            iniciar_hw:
            force:

    """
    global _sesion_actual
    if not _sesion_actual or force:
        _sesion_actual = Sesion(iniciar_hw=iniciar_hw)
    return _sesion_actual
