import textwrap
from copy import copy

from msa.core.imaging import Imagen, jinja_env
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.documentos.actas import Recuento


class TextoActaRecuento(Imagen):
    def __init__(
        self, recuento: Recuento, mostrar=None, x: int = 0, y: int = 0
    ) -> None:
        super().__init__()
        self._x = x
        self._y = y
        self._recuento = recuento

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        if self.config_vista("en_pantalla"):
            self.offset_top = 370
        else:
            self.offset_top = 0

        self.template = "actas/texto.tmpl"
        self.template_texto = "actas/textos/recuento.tmpl"

        self.render_template()

    def generate_data(self):

        data = {
            "x": self._x,
            "y": self._y,
            "colores": COLORES,
            "mesa": self._recuento.mesa,
            "autoridades": self._recuento.autoridades,
            "en_pantalla": self.config_vista("en_pantalla"),
        }

        if self._recuento.hora is not None:
            data["horas"] = "%02d" % self._recuento.hora["horas"]
            data["minutos"] = "%02d" % self._recuento.hora["minutos"]
        else:
            data["horas"] = ""
            data["minutos"] = ""

        if len(self._recuento.autoridades):
            data["presidente"] = self._recuento.autoridades[0]
        else:
            data["presidente"] = None

        if len(self._recuento.autoridades) > 1:
            data["suplentes"] = self._recuento.autoridades[1:]
            data["cantidad_suplentes"] = len(data["suplentes"])
        else:
            data["suplentes"] = []
            data["cantidad_suplentes"] = 0

        self.data = data
        self.data["texto_acta"] = self._get_texto()

        return data

    def _get_texto(self):
        """
        Devuelve los datos del texto del acta para el template.
        """
        texto = None
        if self.config_vista("texto"):
            # traigo los templates
            uri_tmpl_suplentes = "actas/textos/suplentes.tmpl"
            uri_tmpl_presidente = "actas/textos/presidente.tmpl"
            tmpl_suplentes = jinja_env.get_template(uri_tmpl_suplentes)
            tmpl_presidente = jinja_env.get_template(uri_tmpl_presidente)
            template = jinja_env.get_template(self.template_texto)
            # los renderizo y los meto en data
            self.data["texto_suplentes"] = tmpl_suplentes.render(**self.data)
            self.data["texto_presidente"] = tmpl_presidente.render(**self.data)
            # y le paso todo al template del texto para armar el texto del acta
            self.texto = template.render(**self.data)

            posicion, wrap = MEDIDAS_ACTA["texto"]
            dy = posicion - self.offset_top
            texto = (dy, textwrap.wrap(self.texto, wrap))
        return texto
