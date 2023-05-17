from msa.core.imaging import Imagen
from msa.core.imaging.actas.componentes.seguridad_y_ctx import SeguridadYCtx
from msa.core.imaging.constants import COLORES, MEDIDAS_ACTA
from msa.core.documentos.actas import Recuento
from msa.core.documentos.constants import CIERRE_ESCRUTINIO

from msa.core.imaging.actas.componentes.encabezado_recuento import EncabezadoActaRecuento
from msa.core.imaging.actas.componentes.especiales import (
    EspecialesActa,
)
from msa.core.imaging.actas.componentes.firmas import FirmasActaParaguay
from msa.core.imaging.actas.componentes.qr import QrActa
from msa.core.imaging.actas.componentes.tabla_sin_preferentes_sin_blanco import (
    TablaSinPreferentes,
)
from msa.core.imaging.actas.componentes.ubicaciones import UbicacionActa
from msa.core.imaging.actas.componentes.nro_hoja import NroHoja
from msa.core.imaging.actas.componentes.escudo import Escudo
from msa.core.imaging.actas.componentes.leyenda import Leyenda
from msa.core.imaging.actas.componentes.firmas_recuento import FirmasActaRecuento
from msa.core.imaging.actas.componentes.verificador import Verificador
from msa.core.imaging.actas.componentes.texto_recuento import TextoActaRecuento
from msa.core.imaging.actas.componentes.watermark import Watermark
from msa.core.constants import PATH_IMAGENES_VARS
from os.path import join


class ActaSinPreferencias(Imagen):
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
        self.template = "actas/acta_sin_preferencias.tmpl"
        self.render_template()
        self._height = MEDIDAS_ACTA["alto_recuento"]
        self._width = MEDIDAS_ACTA["ancho"]

    def generate_data(self):
        path_img_escudo = join(PATH_IMAGENES_VARS, "logo_boleta.png")
        svg_escudo = Escudo(path_img_escudo, x=0, y=0).render_svg()

        tsp = EncabezadoActaRecuento(
            self._recuento, self._tipo_acta, self.mostrar, x=0, y=0
        )
        svg_encabezado = tsp.render_svg()

        _pos_inicial = 200
        if self._tipo_acta == CIERRE_ESCRUTINIO:
            svg_verificador = None
        else:
            path_img_verificador = join(PATH_IMAGENES_VARS, "verificador_alta.png")
            tsp = Verificador(path_img_verificador, self.mostrar, x=95, y=_pos_inicial)
            svg_verificador = tsp.render_svg()

        _pos_inicial += tsp.get_height()
        svg_texto = TextoActaRecuento(self._recuento, x=20, y=_pos_inicial).render_svg()

        _pos_inicial += 195
        tsp = TablaSinPreferentes(self._recuento, x=10, y=_pos_inicial)
        svg_tabla_preferentes = tsp.render_svg()

        _pos_inicial = _pos_inicial + tsp.get_height() + self._margen_tabla_especiales
        svg_especiales = EspecialesActa(
            self._recuento,
            self.mostrar,
            self.extra,
            x=10,
            y=_pos_inicial,
        ).render_svg()

        svg_firmas = FirmasActaRecuento(
            self._recuento, self.mostrar, x=10, y=1480
        ).render_svg()

        svg_qr = None
        if self.config("usar_qr"):
            svg_qr = QrActa(self._recuento, self.mostrar, self.qr_img).render_svg()

        svg_nro_hoja = NroHoja(self._recuento, x=690, y=2600).render_svg()

        if self._tipo_acta == CIERRE_ESCRUTINIO:
            svg_leyenda = None
        else:
            svg_leyenda = Leyenda(x=792, y=1380).render_svg()

        svg_watermarks = Watermark().render_svg()

        data = {
            "escudo": svg_escudo,
            "encabezado": svg_encabezado,
            "verificador": svg_verificador,
            "texto": svg_texto,
            "tabla": svg_tabla_preferentes,
            "especiales": svg_especiales,
            "firmas": svg_firmas,
            "qr": svg_qr,
            "colores": COLORES,
            "nro_hoja": svg_nro_hoja,
            "watermarks": svg_watermarks,
            "leyenda": svg_leyenda,
            "medidas": {"width": self._width, "height": self._height},
        }

        return data
