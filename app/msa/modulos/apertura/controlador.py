from urllib.parse import quote
from gi.repository.GObject import timeout_add

from msa.core.settings import USAR_BUFFER_IMPRESION
from msa.modulos.apertura.constants import TEXTOS
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.base.actions import BaseActionController


class Actions(BaseActionController):
    """
    Acciones del controlador de Apertura
    """

    def msg_confirmar_apertura(self, data):
        """
        Muestra el mensaje de confirmar la apertura.

        Args:
            data:
        """
        self.call_async(self.controlador.msg_confirmar_apertura, data)


class Controlador(ControladorBase):

    """
    Controlador para las pantallas de ingreso de datos.

    Attributes:
        textos (tuple): Contiene los mensajes que se muestran en pantalla.
    """

    def __init__(self, modulo):
        """
        Constructor del controlador de interacción.
        
            - Asigna :const:`TEXTOS <modulos.apertura.constants.TEXTOS>` a :attr:`~textos`.
            - Crea la instancia de :meth:`Actions <~Actions>`.

        Arguments:
            modulo (modulos.apertura.Modulo): una referencia al modulo de apertura.

        """
        super(Controlador, self).__init__(modulo)
        self.set_actions(Actions(self))
        self.textos = TEXTOS

    def document_ready(self, data):
        """
        Callback que llama el browser en el document.ready().

        Args:
            data (dict): datos que llegan desde la vista del browser vía Zaguan.
        """
        self.send_constants()
        self._inicializa_pantalla()

    def _inicializa_pantalla(self):
        """
        Inicializa la pantalla de pre-visualización de la Apertura.
        """
        if self.sesion._tmp_apertura is not None:
            mostrar = {"en_pantalla": True}
            imagen_acta = self.sesion._tmp_apertura.a_imagen(svg=True,
                                                             mostrar=mostrar)
            imagen_data = quote(imagen_acta.encode("utf-8"))
            self.set_pantalla_confirmacion(imagen_data)
        else:
            timeout_add(100, self.modulo.salir)

    def set_pantalla_confirmacion(self, imagen):
        """
        Carga la pantalla de confirmación de Apertura.

        Args:
            imagen (svg): Imagen de pre-visualización de la Apertura.
        """
        self.send_command("pantalla_confirmacion_apertura",
                          [("acta_apertura_mesa"), imagen])

    def proxima_acta(self):
        """
        Muesta el botón para imprimir la siguiente acta.
        """
        self.send_command("pantalla_proxima_acta")

    def reimprimir(self):
        """
        Muesta el mensaje de imprimir y manda a imprimir otra Apertura.
        """
        self.send_command("confirmar_apertura")

    def _procesar_callback(self):
        """
        Procesa el callback.
        """
        self.sesion.impresora.remover_consultar_tarjeta()
        self.callback()

    def hide_dialogo(self):
        """
        Esconde el diálogo.
        """
        self.send_command("hide_dialogo")

    def mostrar_imprimiendo(self):
        """
        Muestra el mensaje de Imprimiendo.
        """
        self.send_command("imprimiendo")

    def msg_confirmar_apertura(self, respuesta):
        """
        Muestra el mensaje para confirmar la Apertura.

        Args:
            respuesta (bool): En caso de que sea ``True`` se pasa
                a la pantalla de "Confirmación de Apertura", si es
                ``False`` se pasa a la pantalla anterior.
        """

        self.modulo.play_sonido_tecla()
        if respuesta:
            self.modulo.confirmar_apertura()
        else:
            self.modulo.volver_atras()

    def msg_error_apertura(self, hay_tag=False):
        """
        Muestra el mensaje de error de la apertura.

        En caso de que el parámetro sea ``True`` se carga el
        template "msg_apertura_no_almacenada". Caso contrario,
        si es ``False`` se carga el template "msg_papel_no_puesto".

        Args:
            hay_tag (bool): Expresa si hay un tag introducido.

        """
        if not hay_tag:
            callback_template = "msg_papel_no_puesto"
        else:
            callback_template = "msg_apertura_no_almacenada"
        self.send_command("pantalla_proxima_acta")
        self.cargar_dialogo(callback_template,
                            aceptar=None,
                            cancelar=self.modulo.salir)

    def reintenta_apertura(self, *args, **kwargs):
        """
        Reintenta la impresión de la Apertura.
        """

        self.hide_dialogo()
        self.modulo.confirmar_apertura()

    def get_constants(self):
        """
        Genera las constantes propias de cada módulo.
        """

        constants_dict = {
            "USAR_BUFFER_IMPRESION": USAR_BUFFER_IMPRESION,
            "realizar_apertura": self.modulo.config("realizar_apertura"),
            "usa_login_desde_inicio":
                self.modulo.config("usa_login_desde_inicio"),
        }
        base_constants_dict = self.base_constants_dict()
        base_constants_dict.update(constants_dict)
        return base_constants_dict
