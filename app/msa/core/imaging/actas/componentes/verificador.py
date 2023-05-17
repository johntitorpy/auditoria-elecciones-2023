from copy import copy
from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA
from os.path import exists


class Verificador(Imagen):
    def __init__(self, path_imagen: str, mostrar=None, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self._path_imagen = path_imagen
        self._mostrar = mostrar
        self._x = x
        self._y = y

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/verificador.tmpl"
        self.render_template()

    def generate_data(self):
        x, y, width, height = MEDIDAS_ACTA["verificador"]
        self._width = width
        self._height = height

        data = {
            "x": x if self._x == 0 else self._x,
            "y": y if self._y == 0 else self._y,
            "width": width,
            "height": height,
            "verificador": self._get_verificador(),
            "colores": COLORES,
        }

        return data

    def _get_verificador(self):
        verificador = None
        if exists(self._path_imagen) and not self.config_vista("en_pantalla"):
            verificador = self._get_img_b64(self._path_imagen)

        return verificador

    def get_height(self):
        verificador = self._get_verificador()
        return self._height if verificador is not None else 0
