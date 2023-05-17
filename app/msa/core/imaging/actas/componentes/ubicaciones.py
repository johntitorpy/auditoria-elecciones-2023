import textwrap
from copy import copy

from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA

from pprint import pprint


class UbicacionActa(Imagen):

    def __init__(self, mesa=None, mostrar=None, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self._mesa = mesa
        self._x = x
        self._y = y

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/ubicacion.tmpl"
        self.render_template()

    def generate_data(self) -> object:

        data = {
            'x': self._x,
            'y': self._y,
            "colores": COLORES,
            "i18n": self._get_i18n(),
            "en_pantalla": self.config_vista("en_pantalla"),
            "medidas": self._get_medidas(),
            "codigos_ubicaciones": self.codigo_ubicaciones(),
            "mesa": self._mesa,
            "mesa_escuela": "" if self._mesa.escuela == "" else textwrap.wrap(self._mesa.escuela, 60,
                                                                                break_long_words=False),
            "mesa_municipio": "" if self._mesa.municipio == "" else textwrap.wrap(self._mesa.municipio, 30,
                                                                                    break_long_words=False),
            "mesa_pais": "" if self._mesa.pais == "" else textwrap.wrap(self._mesa.pais, 50, break_long_words=False),
        }

        if self._mesa.numero:
            if len(data["mesa_escuela"]) > 1 and len(data["mesa_municipio"]) > 1:
                alto_bloque = 195
            elif len(data["mesa_escuela"]) > 1 or len(data["mesa_municipio"]) > 1:
                alto_bloque = 180
            elif len(data["mesa_pais"]) > 1 or len(data["mesa_municipio"]) > 1:
                alto_bloque = 185
            else:
                alto_bloque = 165

            data["medidas"]["alto_bloque"] = alto_bloque

        if not data["en_pantalla"]:
            y_ubicaciones = 160
            x_ubicaciones = 10
        else:
            y_ubicaciones = 130
            x_ubicaciones = 40

        data["medidas"]["y_ubicaciones"] = y_ubicaciones
        data["medidas"]["x_ubicaciones"] = x_ubicaciones

        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self) -> object:

        textos = {
            "mesa": _("mesa"),
            "pais": _("py_Pais"),
            "distrito": "Depto",
            "departamento": _("py_Departamento"),
            "localidad": _("py_Localidad"),
            "establecimiento": _("py_Establecimiento"),
        }
        return textos

    def _get_medidas(self) -> object:
        """Devuelve las medidas del acta"""
        medidas = {
            "alto_linea_texto": MEDIDAS_ACTA["alto_linea_texto"],
            "margin_left": MEDIDAS_ACTA["margin_left"],
            "margin_y": 30,

        }

        return medidas

    def codigo_ubicaciones(self) -> object:
        codigos_ubicaciones = {}
        ubicacion = copy(self._mesa)
        while ubicacion:
            codigos_ubicaciones[ubicacion.clase] = ubicacion.codigo.split('.')[-1]
            ubicacion = ubicacion.parent
        return codigos_ubicaciones
