from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.documentos.actas import Recuento


class FirmasActaParaguay(Imagen):
    def __init__(self, recuento: Recuento, tipo_acta: str, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self._recuento = recuento
        self._tipo_acta = tipo_acta
        self._x = x
        self._y = y

        self.template = "actas/firmas_paraguay.tmpl"
        self.render_template()

    def generate_data(self):
        data = {
            "x": self._x,
            "y": self._y,
            "i18n": self._get_i18n(),
            "colores": COLORES,
            "medidas": self._get_medidas(),
            "posiciones": self._get_posiciones(),
        }

        if self._recuento.autoridades:
            data["presidente"] = self._recuento.autoridades[0]
        else:
            data["presidente"] = None

        if len(self._recuento.autoridades) > 1:
            data["suplentes"] = self._recuento.autoridades[1:]
            data["cantidad_suplentes"] = len(data["suplentes"])
        else:
            data["suplentes"] = []
            data["cantidad_suplentes"] = 0

        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self):
        textos = {
            "firmas_autoridades": _("firmas_autoridades"),
            "firmas_fiscales": _("firmas_fiscales"),
            "firmas_fiscales_detalle": _("firmas_fiscales_detalle"),
        }

        return textos

    @staticmethod
    def _get_medidas():
        """Devuelve las medidas del acta."""

        medidas = {
            "alto_encabezado": MEDIDAS_ACTA["alto_encabezado"],
        }
        return medidas

    @staticmethod
    def _get_posiciones():
        """Averigua la ubicacion de cada uno de los elementos del acta."""
        posiciones = {}
        alto_firmas = MEDIDAS_ACTA['alto_firmas']

        posiciones['firmas'] = 0
        # calculamos el final de las firmas
        posiciones['final'] = (posiciones['firmas'] + alto_firmas)

        return posiciones
