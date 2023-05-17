from copy import copy
from msa.core.documentos.actas import PruebaCTX, Recuento
from msa.core.imaging import Imagen
from msa.core.imaging.constants import DEFAULTS_MOSTRAR_ACTA, MEDIDAS_ACTA


class QrActa(Imagen):
    def __init__(self, recuento: Recuento, tipo_acta:str, mostrar=None, x: int = 0, y: int = 0):
        super().__init__()
        self._recuento = recuento
        self._tipo_acta = tipo_acta
        self._qr = self._recuento.a_qr_b64_encoded(self._recuento.grupo_cat, tipo_acta)
        self._x = x
        self._y = y

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/qr.tmpl"
        self.render_template()

    def generate_data(self):
        medidas = self._get_medidas()
        x, y, qr_img, qr_width, qr_height = self._get_qr(medidas['width'])
        medidas.__setitem__("qr_width", qr_width)
        medidas.__setitem__("qr_height", qr_height)

        data = {
            'x': x if self._x == 0 else self._x,
            'y': y if self._y == 0 else self._y,
            "medidas": medidas,
            "qr": qr_img,
        }

        return data

    @staticmethod
    def _get_medidas():
        medidas = {
            "width": MEDIDAS_ACTA["ancho"],
        }
        return medidas

    def _get_qr(self, width):
        """Devuelve los datos del QR para el template."""
        qr = None
        if not self.config_vista("en_pantalla"):
            if self._qr:
                key = "qr_recuento" if self._recuento is not None \
                    else "qr_apertura"
                pos_x, pos_y, pos_w, pos_h = MEDIDAS_ACTA[key]
                qr = [width - pos_x, pos_y, self._qr, pos_w, pos_h]

        return qr

class QrActaCtx(Imagen):

    def __init__(self, acta_ctx: PruebaCTX, x: int = 0, y: int = 0):
        super().__init__()
        self._qr = acta_ctx.a_qr_b64_encoded()
        self._x = x
        self._y = y

        self.template = "actas/qr.tmpl"
        self.render_template()

    def generate_data(self):
        medidas = self._get_medidas()
        x, y, qr_img, qr_width, qr_height = self._get_qr(medidas['width'])
        medidas.__setitem__("qr_width", qr_width)
        medidas.__setitem__("qr_height", qr_height)

        data = {
            'x': x if self._x == 0 else self._x,
            'y': y if self._y == 0 else self._y,
            "medidas": medidas,
            "qr": qr_img,
        }

        return data

    @staticmethod
    def _get_medidas():
        medidas = {
            "width": MEDIDAS_ACTA["ancho"],
        }
        return medidas

    def _get_qr(self, width):
        """Devuelve los datos del QR para el template."""
        key = "qr_recuento" 
        pos_x, pos_y, pos_w, pos_h = MEDIDAS_ACTA[key]
        qr = [width - pos_x, pos_y, self._qr, pos_w, pos_h]

        return qr