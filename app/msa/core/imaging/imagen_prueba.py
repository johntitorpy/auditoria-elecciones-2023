from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA


class ImagenPrueba(Imagen):

    """Clase para la imagen de prueba de impresion."""

    def __init__(self):
        self.template = "test.svg"
        self.render_template()

    def generate_data(self):
        """Genera la data para enviar al template."""
        svg_args = {}
        self._width = MEDIDAS_ACTA["ancho"]
        self._height = MEDIDAS_ACTA["alto_recuento"]
        svg_args['width'] = self._width
        svg_args['height'] = self._height

        self.data = svg_args

        return svg_args


