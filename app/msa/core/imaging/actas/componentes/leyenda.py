from msa.core.imaging import Imagen
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.imaging.constants import COLORES
class Leyenda(Imagen):
    def __init__(
        self, x: int = 0, y: int = 0, width: int=800, height: int=40
    ) -> None:
        super().__init__()
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        self.template = "actas/leyenda.tmpl"
        self.render_template()

    def generate_data(self):
        data = {
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height,
            'i18n': self._get_i18n(),
            'colores': COLORES
        }

        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self):
        textos = {
            "leyenda": _("no_insertar_en_urna"),
        }

        return textos


