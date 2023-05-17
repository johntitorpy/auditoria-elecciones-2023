from os.path import join
from msa.core.constants import PATH_IMAGENES_VARS
from msa.core.imaging import Imagen
from msa.core.imaging.actas.componentes.qr import QrActaCtx
from msa.core.imaging.constants import COLORES, MEDIDAS_ACTA


class ImagenActaCTX(Imagen):
    def __init__(self, acta_ctx):
        """Constructor.

        Argumentos:
            data: datos para rellenar el acta.
            qr: imagen del QR.
        """
        self.template = "actas/acta_prueba_ctx.tmpl"

        self.render_template()
        self._acta_ctx = acta_ctx

    def _get_medidas(self):
        """Devuelve las medidas del acta."""

        alto = MEDIDAS_ACTA["alto_recuento"]

        medidas = {
            "width": MEDIDAS_ACTA["ancho"],
            "height": alto
        }
        return medidas

    def generate_data(self):
        """Genera todos los datos que vamos a necesitar para armar el acta."""
        medidas = self._get_medidas()
        self._width = medidas['width']
        self._height = medidas['height']

        svg_qr = QrActaCtx(self._acta_ctx).render_svg()

        data = {
            "colores": COLORES,
            "verificador": self._get_verificador(),
            "medidas": medidas,
            "width": self._width,
            "height": self._height,
            "i18n": self._get_i18n(),
            "qr": svg_qr
        }

        self.data = data

        return data

    def _get_i18n(self):

        textos = {
            "texto_acta_prueba_ctx_1": _("texto_acta_prueba_ctx_1"),
            "texto_acta_prueba_ctx_2": _("texto_acta_prueba_ctx_2"),
            "texto_acta_prueba_ctx_3": _("texto_acta_prueba_ctx_3")

        }

        return textos

    def _get_verificador(self):
        """Devuelve los datos del verificador para el template."""
        # muestro imagen verificador y corro margen superior hacia abajo
        verif_x, verif_y = MEDIDAS_ACTA["verificador"]
        img_verif = join(PATH_IMAGENES_VARS, 'verificador_alta.png')
        img_verif = self._get_img_b64(img_verif)

        return (verif_x, verif_y, img_verif)
