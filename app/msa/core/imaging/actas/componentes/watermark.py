from msa.core.imaging import Imagen
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.imaging.constants import MEDIDAS_ACTA, DEFAULTS_MOSTRAR_ACTA
from msa.settings import MODO_DEMO
from copy import copy

class Watermark(Imagen):
    def __init__(
        self, watermarks=None, mostrar=None
    ) -> None:
        super().__init__()

        self._watermarks = watermarks
        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/watermark.tmpl"
        self.render_template()

    def generate_data(self):
        data = {
            'watermark': self._get_watermark()
        }

        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_watermark(self):
        """Devuelve el watermark de las actas."""
        watermarks = []
        if MODO_DEMO and not self.config_vista("en_pantalla"):
            # solo muestro la marca de agua si imprimo (con verificador)          
            pos_watermark = MEDIDAS_ACTA['pos_watermark'] if self._watermarks is None else self._watermarks
       
            for posicion in pos_watermark:
                watermark = {
                    "x": posicion[0],
                    "y": posicion[1],
                    "text": _("watermark_text"),
                    "font_size": posicion[2]
                }
                watermarks.append(watermark)
        return watermarks
