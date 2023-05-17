import textwrap
from copy import copy
from typing import List

from msa.core.data.candidaturas import Categoria
from msa.core.documentos.helpers import smart_title
from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE

from msa.core.documentos.actas import Recuento


class EncabezadoActaParaguay(Imagen):
    def __init__(
        self,
        recuento: Recuento,
        tipo_acta: str,
        mostrar: dict,
        extra: dict,
        x: int = 0,
        y: int = 0,
    ) -> None:
        super().__init__()
        self._recuento = recuento
        self._tipo_acta = tipo_acta
        self._mesa = recuento.mesa
        self._extra = extra
        self._x = x
        self._y = y
        self._height = 0

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/encabezado.tmpl"
        self.render_template()

    def generate_data(self):
        data = {
            "x": self._x,
            "y": self._y,
            "i18n": self._get_i18n(),
            "colores": COLORES,
            "mesa": self._mesa,
            "medidas": self._get_medidas(),
            "encabezado": self._get_encabezado(),
        }
        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self):
        textos = {
            "agrupaciones": _("agrupaciones"),
        }

        return textos

    @staticmethod
    def _get_medidas():
        """Devuelve las medidas del acta."""

        medidas = {
            "alto_encabezado": MEDIDAS_ACTA["alto_encabezado"],
        }
        return medidas

    def _get_encabezado(self):
        """
        Devuelve los datos del encabezado
        """

        datos = {
            "nombre_acta": self._get_titulo(),
            "texto": self._get_texto_encabezado(),
        }

        return datos

    def _get_titulo(self) -> List[str]:
        """Devuelve el título del acta

        Returns:
            str: titulo del acta
        """
        _, wrap = MEDIDAS_ACTA["titulo"]

        titulo, _, _ = self._recuento.generar_titulo(self._tipo_acta)

        if self.config("encabezado_acta_recuento_muestra_nombre_cargos"):
            titulo = [
                titulo,
                ";".join(
                    [
                        smart_title(cat.nombre)
                        for cat in Categoria.many(
                            sorted="posicion", id_grupo=self._recuento.grupo_cat
                        )
                    ]
                ),
            ]

        nombre_acta = []
        for t in titulo:
            nombre_acta.append(textwrap.wrap(t, wrap))

        return nombre_acta

    def _get_texto_encabezado(self):
        """Devuelve los datos de los titulos para el template."""
        lineas = []

        if not self.config_vista("en_pantalla"):
            # Esto sería un for si no cambiara tanto de eleccion a eleccion
            # probamos varias cosas con los años, esta es la solucion mas
            # customisable
            lineas = []
            for x in range(1, 5):
                if _(f"encabezado_acta_{x}") != f"encabezado_acta_{x}":
                    lineas.append(_(f"encabezado_acta_{x}"))

            self._height = 130 if len(lineas) == 4 else 105

        return lineas

    def get_height(self):
        return self._height
