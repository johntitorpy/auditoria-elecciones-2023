from msa.core.imaging import Imagen
from msa.core.imaging.constants import COLORES, MEDIDAS_ACTA, CONFIG_BOLETA_APERTURA

from msa.core.imaging.actas.componentes.encabezado_apertura import (
    EncabezadoActaApertura,
)
from msa.core.imaging.actas.componentes.qr import QrActa
from msa.core.imaging.actas.componentes.escudo import Escudo
from msa.core.imaging.actas.componentes.verificador import Verificador
from msa.core.imaging.actas.componentes.texto_apertura import TextoActaApertura
from msa.core.imaging.actas.componentes.firmas_apertura import FirmasActaApertura
from msa.core.imaging.actas.componentes.qr_apertura import QrActaApertura
from msa.core.imaging.actas.componentes.watermark import Watermark
from msa.core.constants import PATH_IMAGENES_VARS
from os.path import join


class ActaApertura(Imagen):
    def __init__(self, apertura, mostrar=None, extra=None, qr_img=None):
        super().__init__()
        self._tipo_acta = CONFIG_BOLETA_APERTURA["tipo"]
        self._apertura = apertura
        self._mostrar = mostrar
        self._extra = extra
        self.qr_img = qr_img
        self.template = "actas/acta_apertura.tmpl"
        self.render_template()
        self._width = MEDIDAS_ACTA["ancho"]
        self._height = (
            MEDIDAS_ACTA["alto_apertura"]
            if not self.config_vista("en_pantalla")
            else MEDIDAS_ACTA["alto_apertura_en_pantalla"]
        )

    def generate_data(self):
        path_img_escudo = join(PATH_IMAGENES_VARS, "logo_boleta.png")

        tsp = Escudo(path_img_escudo, x=0, y=0)
        svg_escudo = tsp.render_svg()

        tsp = EncabezadoActaApertura(self._apertura,  self._mostrar, x=0, y=0)
        svg_encabezado = tsp.render_svg()

        _pos_inicial = 200 if not self.config_vista("en_pantalla") else tsp.get_height()
        path_img_verificador = join(PATH_IMAGENES_VARS, "verificador_alta.png")
        tsp = Verificador(path_img_verificador, self._mostrar, x=100, y=_pos_inicial)
        svg_verificador = tsp.render_svg()
        
        _pos_inicial += tsp.get_height()
        tsp = TextoActaApertura(self._apertura, x=20, y=_pos_inicial)
        svg_texto = tsp.render_svg()

        tsp = FirmasActaApertura(self._apertura, self._mostrar, x=20, y=700)
        svg_firmas = tsp.render_svg()

        tsp = QrActaApertura(self._apertura, self._mostrar)
        svg_qr = tsp.render_svg()

        # (x, y font_size)
        watermarks = [
            (-350, 500, 30),
            (-650, 900, 30),
            (-950, 1300, 30),
        ]
        tsp = Watermark(watermarks, self._mostrar)
        svg_watermarks = tsp.render_svg()

        data = {
            "escudo": svg_escudo,
            "encabezado": svg_encabezado,
            "verificador": svg_verificador,
            "texto": svg_texto,
            "firmas": svg_firmas,
            "qr": svg_qr,
            "colores": COLORES,
            "watermarks": svg_watermarks,
            "medidas": {"width": self._width, "height": self._height},
            "en_pantalla": self.config_vista("en_pantalla"),
        }

        return data
