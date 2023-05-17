from msa.core.data.candidaturas import Categoria
from msa.core.documentos.actas import Recuento

from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES


class NroHoja(Imagen):
    def __init__(
        self, recuento: Recuento, x: int = 0, y: int = 0
    ) -> None:
        super().__init__()
        self._recuento = recuento
        self._x = x
        self._y = y

        self.template = "actas/nro_hoja.tmpl"
        self.render_template()

    def generate_data(self):
        categorias = Categoria.many(sorted="posicion")
        grupos_categorias = set([cat.id_grupo for cat in categorias])
        hoja = None
        if self._recuento.grupo_cat is None:
            hoja = 1
        else:
            for idx, id_grupo in enumerate(grupos_categorias, start=1):
                if id_grupo==self._recuento.grupo_cat:
                    hoja = idx
                
        data = {
            "x": self._x,
            "y": self._y,
            "nro_hoja": hoja,
            "total_hojas": len(grupos_categorias),
            "colores": COLORES,
        }
        return data

