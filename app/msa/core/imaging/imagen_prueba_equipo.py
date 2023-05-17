import os
from msa.core.imaging import Imagen
from msa.core.imaging.helpers import init_jinja
import time
from os.path import join
from msa.core.constants import PATH_IMAGENES_VARS
from msa.core.imaging.constants import MEDIDAS_BOLETA, MEDIDA_BOLETA_PRUEBA_EQUIPO


from msa.core.logging import get_logger

logger = get_logger("imagen_prueba_equipo")

jinja_env = init_jinja()


class ImagenPruebaEquipo(Imagen):
    """Clase para la imagen de la boleta."""

    def __init__(self, data):
        self.template = "boletas/boleta_prueba_equipo.tmpl"
        self.render_template()
        self.medidas = self._get_medidas()
        self.data = None

    def generate_data(self):
        """Genera la data para mandar al template de la boleta."""

        self._width = self.medidas["ancho_boleta"]
        self._height = self.medidas["alto_con_verif"]
        data = {}

        data["verificador"] = self._get_verificador()
        data["voto_recortado"] = self._get_voto_recortado()
        data["hora"] = self._get_time()
        data["fecha"] = self._get_date()

        data["width"] = self._width
        data["height"] = self._height
        data["margen_izq"] = self.medidas["margen_izq"]
        data["multiplicador_fz"] = self.medidas["multiplicador_fz"]
        self.data = data
        return data

    def _get_medidas(self):
        """Devuelve las medidas de la boleta."""
        return MEDIDA_BOLETA_PRUEBA_EQUIPO

    def _get_voto_recortado(self):
        """Devuelve los datos del verificador para el template."""
        img_path = join(PATH_IMAGENES_VARS, "voto_recortado.png")
        img_link = self._get_img_b64(img_path)

        pos_voto = self.medidas["pos_voto_recortado"]
        voto_size = self.medidas["voto_size"]
        font_size = self.medidas["fs_verificador"]
        voto_recortado = (
            pos_voto[0],
            pos_voto[1],
            img_link,
            voto_size[0],
            voto_size[1],
        )

        return voto_recortado

    def _get_verificador(self):
        """Devuelve los datos del verificador para el template."""
        img_path = join(PATH_IMAGENES_VARS, "verificador_alta.png")
        img_link = self._get_img_b64(img_path)

        pos_verif = self.medidas["pos_verif"]
        verif_size = self.medidas["verif_size"]
        font_size = self.medidas["fs_verificador"]
        verificador = (
            pos_verif[0] + self.medidas["margen_izq"],
            pos_verif[1],
            img_link,
            verif_size[0],
            verif_size[1],
            _("verifique"),
            _("su_voto"),
            font_size,
        )
        return verificador

    def _get_time(self):
        """obtiene hora de la impresion de la boleta."""
        return time.strftime("%I:%M:%S")

    def _get_date(self):
        """obtiene fecha de la impresion de la boleta."""
        return time.strftime("%Y-%m-%d")
