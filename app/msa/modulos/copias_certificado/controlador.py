"""Controlador para el modulo de ingreso de datos."""
from urllib.parse import quote

from msa.core.data import Ubicacion
from msa.core.data.constants import TIPO_DOC
from msa.core.documentos.autoridades import Autoridad
from msa.core.documentos.actas import Apertura
from msa.core.documentos.settings import CANTIDAD_SUPLENTES
from msa.core.imaging.constants import (CONFIG_BOLETA_APERTURA,
                                        CONFIG_BOLETA_CIERRE,
                                        CONFIG_BOLETA_TRANSMISION)
from msa.core.imaging.reverso import ImagenReversoBoleta
from msa.core.settings import USAR_BUFFER_IMPRESION
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.constants import (E_INGRESO_ACTA, E_INGRESO_DATOS, E_MESAYPIN,
                                   MODULO_APERTURA, MODULO_INICIO, E_CONFIRMACION,
                                   MODULO_RECUENTO, MODULO_TOTALIZADOR, 
                                   SUBMODULO_MESA_Y_PIN_INICIO, MODULO_MENU)
from msa.modulos.copias_certificado.constants import ERRORES, TEXTOS, ACTA_A_APOYAR
from msa.settings import DEBUG, MODO_DEMO


class Actions(BaseActionController):
    """Actions del controlador de interaccion/"""
    pass
    
class Controlador(ControladorBase):

    """Controller para las pantallas de ingreso de datos."""

    def __init__(self, modulo):
        """Constructor del controlador de interaccion."""
        super(Controlador, self).__init__(modulo)
        self._intento = 0
        self.set_actions(Actions(self))
        self.MSG_DEFAULT = _("introduzca_acta_cierre")
        self.MSG_ESPERE = _("aguarde_procesando_acta")
        self.mensaje = self.MSG_DEFAULT
        self.textos = TEXTOS

    def document_ready(self, data):
        """Callback que llama el browser en el document.ready()"""
        self._inicializa_pantalla()

    def set_imagen_acta(self):
        """Selecciona config de svg para el modulo."""

        self.imagen_acta = ImagenReversoBoleta(CONFIG_BOLETA_CIERRE).render_svg()

    def _inicializa_pantalla(self):
        """
        Prepara la primera pantalla de la interacción ocultando todos
        los elementos innecesarios del template y mostrando la imagen de la
        boleta.
        """
        self.send_constants()
        self.set_imagen_acta()

        self.mensaje = self.MSG_DEFAULT

        self.set_pantalla()
        self.send_command("show_body")
        self.modulo.rampa.expulsar_boleta()

    def set_cargando_recuento(self):
        """Muestra la pantalla de cargando el recuento."""
        mensaje = _("cargando_recuento")
        actas_a_copiar = self.modulo.config("actas_a_copiar")
        if len(actas_a_copiar)>1:
            self.send_command("pantalla_seleccion_acta",
                          {"actas_a_copiar": actas_a_copiar})
        else:
            self.modulo.seleccionar_acta_a_copiar(actas_a_copiar[0])
            self.send_command("pantalla_carga_recuento",
                            {"mensaje": mensaje,
                            "acta_a_copiar": actas_a_copiar[0]})

    def set_pantalla(self, data=None):
        """Setea la pantalla de acuerdo al estado actual."""
        if data is None:
            data = {}

        self.set_cargando_recuento()

        self.send_constants()    
    
    def set_mensaje(self, mensaje):
        """Cambia el mensaje de la pantalla de ingreso de acta."""
        self.mensaje = mensaje
        self.send_command("set_mensaje", mensaje)

    def set_pantalla_confirmacion(self, imagen):
        """Carga la pantalla de confirmacion de apertura."""
        self.send_command("pantalla_confirmacion_apertura",
                          [_("acta_apertura_mesa"), imagen])
        
    def seleccionar_acta_a_copiar(self, acta_a_copiar=None):
        self.modulo.seleccionar_acta_a_copiar(acta_a_copiar)
        if acta_a_copiar == None:
            actas_a_copiar = self.modulo.config("actas_a_copiar")
            return self.send_command("pantalla_seleccion_acta",
                                     {"actas_a_copiar": actas_a_copiar})
        self.send_command("pantalla_carga_recuento",
                            {"acta_a_copiar": acta_a_copiar})

    def mensaje_inicial(self):
        """Establece el mensaje inicial."""
        self.set_mensaje(self.MSG_DEFAULT)

    def _procesar_callback(self):
        """Procesa el callback."""
        self.sesion.impresora.remover_consultar_tarjeta()
        self.callback()

    def hide_dialogo(self):
        """Esconde el dialogo."""
        self.send_command("ocultar_mensaje")
        self.send_command("hide_dialogo")
        self.send_command("restaurar_foco_invalido")

    
    def get_constants(self):
        """Genera las constantes propias de cada modulo."""
        local_constants = {
            "tipo_doc": [(TIPO_DOC.index(tipo), tipo) for tipo in TIPO_DOC],
            "mensajes_error": dict([(trans, _(trans)) for trans in ERRORES]),
            "cantidad_suplentes": CANTIDAD_SUPLENTES,
            "usa_tildes": self.modulo.config("teclado_usa_tildes"),
            "USAR_BUFFER_IMPRESION": USAR_BUFFER_IMPRESION,
            "actas_a_copiar": self.modulo.config("actas_a_copiar"),
            "acta_a_apoyar": ACTA_A_APOYAR,
        }
        constants_dict = self.base_constants_dict()
        constants_dict.update(local_constants)
        return constants_dict
