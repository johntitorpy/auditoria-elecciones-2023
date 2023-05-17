import os
from base64 import encodestring

from msa.core.config_manager import Config
from msa.core.imaging.helpers import init_jinja, xml2pil
from msa.core.logging import get_logger


logger = get_logger("imaging")
jinja_env = init_jinja()


class Imagen(object):

    """Clase base para las imagenes del modulo."""
    renderer = None
    def __init__(self) -> None:
        self._config = {}

    @classmethod
    def get_renderer(cls):
        from msa.core.imaging.renderer import Renderer
        from msa.modulos.constants import PATH_TEMPLATES_GUI
        if cls.renderer is None:
            cls.renderer = Renderer(os.path.join(PATH_TEMPLATES_GUI, 'boleta.html'))
        return cls.renderer

    def config_vista(self, key):
        return self._mostrar.get(key, False)

    def generate_data(self):
        """Genera la data para enviar al template."""
        raise NotImplementedError("You must implement on subclass")

    def render_template(self):
        self.rendered_template = jinja_env.get_template(self.template)

    def render_svg(self):
        """Renderiza el SVG."""
        data = self.generate_data()
        xml = self.rendered_template.render(**data)
        return xml

    def render_image(self):
        """Renderiza la imagen."""
        xml = self.render_svg()
        return xml2pil(xml, self._width, self._height)

    def render(self, svg):
        ret = None
        if svg:
            ret = self.render_svg()
        else:
            ret = self.render_image()

        return ret

    def _get_img_b64(self, img_path):
        """Devuelve la imagen en base64 formato browser."""
        image = open(img_path, 'rb')
        img_data = image.read()
        img_data = encodestring(img_data)
        image.close()
        img_link = "data:image/png;base64,%s" % img_data.decode()
        return img_link

    def config(self, key, id_ubicacion=None):
        
        if id_ubicacion not in self._config:
            self._config[id_ubicacion] = Config(["common", "imaging"], id_ubicacion)
            
        value, file_ = self._config[id_ubicacion].data(key)
        logger.debug("Trayendo config {}: {} desde {}".format(key, value,
                                                                file_))
        
        return value
