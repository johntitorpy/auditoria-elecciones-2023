from copy import copy
from msa.core.documentos.actas import PruebaCTX, Apertura
from msa.core.imaging import Imagen
from msa.core.imaging.constants import DEFAULTS_MOSTRAR_ACTA, MEDIDAS_ACTA


class QrActaApertura(Imagen):
    def __init__(self, apertura: Apertura, mostrar=None, x: int = 0, y: int = 0):
        super().__init__()
        self._apertura = apertura
        self._qr = self._apertura.a_qr_b64_encoded()
        self._x = x
        self._y = y

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/qr.tmpl"
        self.render_template()

    def generate_data(self):
        medidas = self._get_medidas()
        datos_qr = self._get_qr(medidas["width"])
        if datos_qr is not None:
            x, y, qr_img, qr_width, qr_height = self._get_qr(medidas["width"])
            medidas.__setitem__("qr_width", qr_width)
            medidas.__setitem__("qr_height", qr_height)

            data = {
                "x": x if self._x == 0 else self._x,
                "y": y if self._y == 0 else self._y,
                "medidas": medidas,
                "qr": qr_img,
            }
        else:
            data = {"qr": None}
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
                pos_x, pos_y, pos_w, pos_h = MEDIDAS_ACTA["qr_apertura"]
                qr = [width - pos_x, pos_y, self._qr, pos_w, pos_h]

        return qr
