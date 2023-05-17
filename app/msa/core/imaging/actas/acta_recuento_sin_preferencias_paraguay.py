from msa.core.imaging import Imagen
from msa.core.imaging.actas.componentes.seguridad_y_ctx import SeguridadYCtx
from msa.core.imaging.constants import COLORES, MEDIDAS_ACTA
from msa.core.documentos.actas import Recuento

from msa.core.imaging.actas.componentes.encabezado import EncabezadoActaParaguay
from msa.core.imaging.actas.componentes.especiales_con_blanco import (
    EspecialesConBlancoActa,
)
from msa.core.imaging.actas.componentes.firmas import FirmasActaParaguay
from msa.core.imaging.actas.componentes.qr import QrActa
from msa.core.imaging.actas.componentes.tabla_sin_preferentes_sin_blanco import (
    TablaSinPreferentesSinBlanco,
)
from msa.core.imaging.actas.componentes.ubicaciones import UbicacionActa
from msa.core.imaging.actas.componentes.nro_hoja import NroHoja
from msa.core.imaging.actas.componentes.escudo import Escudo
from msa.core.imaging.actas.componentes.leyenda import Leyenda
from msa.core.imaging.actas.componentes.watermark import Watermark
from msa.core.constants import PATH_IMAGENES_VARS
from os.path import join


class ActaSinPreferenciasParaguay(Imagen):
    def __init__(
        self, recuento: Recuento, tipo_acta: str, mostrar=None, extra=None, qr_img=None
    ):
        super().__init__()
        self._recuento = recuento
        self._tipo_acta = tipo_acta
        self.mostrar = mostrar
        self.extra = extra
        self.qr_img = qr_img
        self._margen_tabla_especiales = 20
        self._margen_firmas = 10
        self.template = "actas/acta_sin_preferencias_paraguay.tmpl"
        self.render_template()
        self._height = MEDIDAS_ACTA["alto_recuento"]
        self._width = MEDIDAS_ACTA["ancho"]

    def generate_data(self):
        path_img_escudo = join(PATH_IMAGENES_VARS, "logo_boleta.png")
        tsp = Escudo(path_img_escudo, x=0, y=0)
        svg_escudo = tsp.render_svg()

        tsp = EncabezadoActaParaguay(
            self._recuento, self._tipo_acta, self.mostrar, self.extra
        )
        svg_encabezado = tsp.render_svg()

        _pos_inicial = tsp.get_height()
        syctx = SeguridadYCtx(self._recuento, self._tipo_acta, x=550, y=_pos_inicial)
        svg_syctx = syctx.render_svg()

        _pos_inicial += 55
        tsp = UbicacionActa(self._recuento.mesa, self.mostrar, x=10, y=_pos_inicial)
        svg_ubicacion = tsp.render_svg()

        _pos_inicial += 180
        tsp = TablaSinPreferentesSinBlanco(self._recuento, x=10, y=_pos_inicial)
        svg_tabla_preferentes = tsp.render_svg()

        _pos_inicial = _pos_inicial + tsp.get_height() + self._margen_tabla_especiales
        tsp = EspecialesConBlancoActa(
            self._recuento,
            self.mostrar,
            self.extra,
            x=10,
            y=_pos_inicial,
        )
        svg_especiales = tsp.render_svg()

        _pos_inicial += tsp.get_height()
        tsp = FirmasActaParaguay(
            self._recuento,
            self._tipo_acta,
            y=_pos_inicial + self._margen_firmas,
        )
        svg_firmas = tsp.render_svg()

        svg_qr = None
        if self.config("usar_qr"):
            tsp = QrActa(self._recuento, self.mostrar, self.qr_img)
            svg_qr = tsp.render_svg()

        tsp = NroHoja(self._recuento, x=690, y=2600)
        svg_nro_hoja = tsp.render_svg()

        
        tsp = Watermark()
        svg_watermarks = tsp.render_svg()

        data = {
            "escudo": svg_escudo,
            "encabezado": svg_encabezado,
            "seguridad_y_ctx": svg_syctx,
            "ubicacion": svg_ubicacion,
            "tabla": svg_tabla_preferentes,
            "especiales": svg_especiales,
            "firmas": svg_firmas,
            "qr": svg_qr,
            "colores": COLORES,
            "nro_hoja": svg_nro_hoja,
            "watermarks": svg_watermarks,
            "medidas": {"width": self._width, "height": self._height},
        }

        return data
