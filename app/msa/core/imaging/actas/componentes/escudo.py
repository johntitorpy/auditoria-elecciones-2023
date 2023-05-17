from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES
from os.path import exists

class Escudo(Imagen):
    def __init__(
        self, path_imagen: str, x: int = 0, y: int = 0
    ) -> None:
        super().__init__()
        self._x = x
        self._y = y
        self._path_imagen = path_imagen

        self.template = "actas/escudo.tmpl"
        self.render_template()

    def generate_data(self):
        x, y, width, height = MEDIDAS_ACTA["escudo"]
        data = {
            'x': x if self._x == 0 else self._x,
            'y': y if self._y == 0 else self._y,
            'width': width,
            "height": height,
            "escudo": self._get_escudo(),
            "colores": COLORES
        }

        return data

    def _get_escudo(self):
        if exists(self._path_imagen):
            return self._get_img_b64(self._path_imagen)


