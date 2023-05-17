from msa.core.data.candidaturas import Categoria
from msa.core.documentos.actas import Recuento

from msa.core.imaging import Imagen
from msa.core.imaging.settings import ACTAS_CON_CTX
from msa.core.imaging.constants import MEDIDAS_ACTA


class SeguridadYCtx(Imagen):
    def __init__(
        self, recuento: Recuento, tipo_acta: str, x: int = 0, y: int = 0
    ) -> None:
        super().__init__()
        self._recuento = recuento
        self._tipo_acta = tipo_acta
        self._x = x
        self._y = y

        self.template = "actas/seguridad_y_ctx.tmpl"
        self.render_template()

    def generate_data(self):
        cod_seg = None
        cargos = Categoria.many(id_grupo=self._recuento.grupo_cat)

        cod_seg = " ".join(
            [
                str(self._recuento.mesa.codigos_seguridad[cargo.codigo])
                if cargo.codigo in self._recuento.mesa.codigos_seguridad
                else ""
                for cargo in cargos
            ]
        )

        data = {
            "x": self._x,
            "y": self._y,
            "codigo_seguridad": cod_seg,
            "ctx": self._recuento.mesa.ctx if self._tipo_acta in ACTAS_CON_CTX else None,
            "separacion": MEDIDAS_ACTA['separacion_ctx']
        }
        return data

