from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_BOLETA
from msa.core.logging import get_logger


logger = get_logger("imaging")


class BoletaInvalida(Imagen):

    """Clase para la imagen de prueba de impresion."""

    def __init__(self, codigo_error=None):
        """
        Utilizamos un template especial para las boletas
        inváidas
        """
        self.template = "boletas/invalida.tmpl"
        self.render_template()
        self.medidas = self._get_medidas()
        self._width = self.medidas["ancho_boleta"]
        self._height = self.medidas["alto_boleta"]
        self.codigo_error = codigo_error
        self.data = None

    @staticmethod
    def _get_medidas():
        """Devuelve las medidas de la boleta."""
        return MEDIDAS_BOLETA

    def generate_data(self):
        """Genera la data para enviar al template."""
        self.data = {
            "width": self._width,
            "height": self._height,
            "titulo_no_valido": "Boletín de Voto inválido.",
            "subtitulo_no_valido": "Devuelva este Boletín al Miembro de Mesa ",
            "subtitulo_no_valido_1": "y solicite un nuevo Boletín de Voto",
            "codigo_error": self.codigo_error,
        }

        return self.data
