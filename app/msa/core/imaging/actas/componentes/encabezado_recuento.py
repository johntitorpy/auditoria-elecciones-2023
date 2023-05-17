from copy import copy

from msa.core.documentos.helpers import smart_title
from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE

from msa.core.documentos.actas import Recuento


class EncabezadoActaRecuento(Imagen):
    def __init__(
        self,
        recuento: Recuento,
        tipo_acta: str,
        mostrar: dict = {},
        extra: dict = {},
        x: int = 0,
        y: int = 0,
        width: int = 722,
        height: int = 55,
    ) -> None:
        super().__init__()
        self._recuento = recuento
        self._mostrar = mostrar
        self._tipo_acta = tipo_acta
        self._extra = extra
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/encabezado_recuento.tmpl"
        self.render_template()

    def generate_data(self):
        data = {
            "x": self._x,
            "y": self._y,
            "i18n": self._get_i18n(),
            "colores": COLORES,
            "mesa": self._recuento.mesa,
            "medidas": self._get_medidas(),
            "encabezado": self._get_encabezado(),
            "en_pantalla": self.config_vista("en_pantalla"),
        }
        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self) -> dict:
        titulo, leyenda, verificador = self._recuento.generar_titulo(self._tipo_acta)
        textos = {
            "titulo": titulo,
            "mesa": _("mesa"),
        }

        return textos

    def _get_medidas(self) -> dict:
        """Devuelve las medidas del acta."""

        medidas = {
            "width": self._width,
            "height": self._height,
            "margin_left": MEDIDAS_ACTA["margin_left"],
        }
        return medidas

    def _get_encabezado(self):
        """
        Devuelve los datos del encabezado
        """

        datos = {
            "texto": self._get_texto_encabezado(),
        }

        return datos

    def _get_texto_encabezado(self):
        """Devuelve los datos de los titulos para el template."""
        lineas = []
        alto_linea = 25
        if not self.config_vista("en_pantalla"):
            encabezados = [1, 2, 3, 4]
            for x in encabezados:
                if _(f"encabezado_acta_{x}") != f"encabezado_acta_{x}":
                    lineas.append(_(f"encabezado_acta_{x}"))

        self._height += len(lineas) * alto_linea
        return lineas

    def get_height(self):
        # le sumo el alto de la mesa
        return self._height + 40
