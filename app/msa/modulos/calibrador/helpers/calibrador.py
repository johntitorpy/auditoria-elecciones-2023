from __future__ import absolute_import
from __future__ import print_function

from random import randint

from msa.modulos.calibrador.helpers import scale_axis, calc_quadrant
from msa.modulos.calibrador.helpers.configurar import XInput, XInputCalibrationMatrix
from msa.modulos.calibrador.settings import FAKE_DEV, INIT_LIBINPUT_PROP_VALUES
from msa.core.logging import get_logger

logger = get_logger('helpers_calibrador')

class Calibrador:
    """ Clase principal de calibración. """

    def __init__(self):
        """
        Constructor en el cual se establecen algunas configuraciones iniciales
        para la pantalla, clicks y acciones de calibración.
        """
        # Screen properties
        self.width = None
        self.height = None

        # Clicks configurations
        self.blocks = 8

        self.clicks_realizados = {}

        # Getting device base properties
        if FAKE_DEV:
            self.device = 'fake'
            self.old_prop_value = [0, 1000, 0, 1000]
        else:
            self.__obtener_dispositivo()

    def __obtener_dispositivo(self):
        """
            Carga un dispositivo desde XInput que sea posible calibrar.
            En caso de que haya más de un dispositivo conectado, se seleccionará
            el último de ellos.

            .. todo:: Si no detecta dispositivo debería llamar a un error en el controlador.
        """
        devices = XInput.get_device_with_prop('libinput Calibration Matrix',
                                            False)
        node = -1
        _devices = []
        for device in devices:
            if int(XInput.get_prop(device[1], 'Device Node')[0][-2]) >= node:
                _devices = [device]
        devices = _devices
        print(devices)
        if not devices:
            # Acá debería llamar a un error en el controller
            pass
        elif len(devices) > 1:
            # Acá se debería ver de filtrar por el nombre de los dispositivos
            # que conocemos para evitar calibrar el teclado
            print("More than one devices detected. Using lastone.")

        # Get device with format (Name, DevID, setted)
        self.device = devices[-1][1]
        self.__get_device_prop_range()
        # This reset calibration to defaults values because recalibration
        # errors
        self.__reset_device_calibration()

    def __get_device_prop_range(self):
        """
        Obtiene el rango de valores de la propiedad de calibración del
        dispositivo.
        """
        self.old_prop_value = XInput.get_prop(self.device, 'libinput Calibration Matrix (')
        self.init_prop_values = INIT_LIBINPUT_PROP_VALUES

    def __reset_device_calibration(self):
        """ Reset the calibration data of the device.
        """
        if FAKE_DEV:
           return
        XInput.set_prop(self.device, '"libinput Calibration Matrix"',
                        '{0} {1} {2} {3} {4} {5} {6} {7} {8}'.format(
                            float(self.init_prop_values[0]),
                            float(self.init_prop_values[1]),
                            float(self.init_prop_values[2]),
                            float(self.init_prop_values[3]),
                            float(self.init_prop_values[4]),
                            float(self.init_prop_values[5]),
                            float(self.init_prop_values[6]),
                            float(self.init_prop_values[7]),
                            float(self.init_prop_values[8])
                        ))

    def set_screen_prop(self, width, height):
        """
        Establece ``width`` y ``height`` de la pantalla, obtiene los puntos
        calculados y la separación entre ellos.

        Args:
            width (int): Ancho de la pantalla.
                Normalmente el valor que se recibe está establecido en
                :const:`SCREEN_SIZE <modulos.gui.settings.SCREEN_SIZE>`.

            height (int): Alto de la pantalla.
                Normalmente el valor que se recibe está establecido en
                :const:`SCREEN_SIZE <modulos.gui.settings.SCREEN_SIZE>`.
        """

        self.width = width
        self.height = height

        block_x = width / self.blocks
        block_y = height / self.blocks

        self.puntos_calculados = {
            'tl': (block_x, block_y),
            'bl': (block_x, block_y * 7),
            'tr': (block_x * 7, block_y),
            'br': (block_x * 7, block_y * 7)
        }

    def generar_punto_verificacion(self):
        """
        Genera aleatoriamente un punto de verificación.

        Returns:
            Tuple[int, int]:
            Coordenadas x,y del punto de verificación.

        """
        block_x = self.width // self.blocks
        block_y = self.height // self.blocks

        seccion = randint(0, 3)
        if seccion == 0:
            pos_x = randint(2 * block_x, 6 * block_x)
            pos_y = randint(1 * block_y, 2 * block_y)
        elif seccion == 1:
            pos_x = randint(5 * block_x, 6 * block_x)
            pos_y = randint(1 * block_y, 2 * block_y)
        elif seccion == 2:
            pos_x = randint(2 * block_x, 6 * block_x)
            pos_y = randint(6 * block_y, 7 * block_y)
        else:
            pos_x = randint(2 * block_x, 3 * block_x)
            pos_y = randint(1 * block_y, 7 * block_y)

        return (pos_x, pos_y)

    def reiniciar(self):
        """
        Reinicia todos los datos de calibración.
        """
        self.clicks_realizados = {}
        self.__reset_device_calibration()
        self.set_screen_prop(self.width, self.height)

    def registrar_clicks(self, listado_clicks):
        """
        Registra un click hecho por el usuario y retorna un error
        en caso de ser necesario.

        Args:
            listado_clicks (?): Son los clicks que se hicieron durante
                la calibración.

        """
        self.clicks_realizados = listado_clicks

    def __escalar_ejes(self):
        """
        Obtiene los nuevos ejes calculados.
        Esto es se hace utilizando los valores viejos de los ejes y los nuevos
        clicks que se hicieron en el proceso de calibración.
        """

        # Screen properties
        width = self.width
        height = self.height

        # Old calibration data
        old_xmin = int(float(self.old_prop_value[0]))
        old_xmax = int(float(self.old_prop_value[1]))
        old_ymin = int(float(self.old_prop_value[2]))
        old_ymax = int(float(self.old_prop_value[3]))

        clicks = self.clicks_realizados
        clicks_x = [clicks[punto][0] for punto in clicks]
        clicks_y = [clicks[punto][1] for punto in clicks]
        clicks_x.sort()
        clicks_y.sort()

        # # Verifying the axes corresponding
        x_min = float(clicks_x[0] + clicks_x[1])/2
        x_max = float(clicks_x[2] + clicks_x[3])/2
        y_min = float(clicks_y[0] + clicks_y[1])/2
        y_max = float(clicks_y[2] + clicks_y[3])/2

        # Swapping axes if necessary
        if (abs(clicks['tr'][0] - clicks['tl'][0]) <
                abs(clicks['bl'][1] - clicks['tl'][1])):
            x_min, y_min = y_min, x_min
            x_max, y_max = y_max, x_max

        # Calculating separation of dot axes
        block_x = float(width) / self.blocks
        block_y = float(height) / self.blocks

        # Calculating the new calibration data
        scale_x = (x_max - x_min) / (width - 2 * block_x)
        x_min -= block_x * scale_x
        x_max += block_x * scale_x
        scale_y = (y_max - y_min) / (height - 2 * block_y)
        y_min -= block_y * scale_y
        y_max += block_y * scale_y

        self.x_min = scale_axis(x_min, old_xmax, old_xmin, width, 0)
        self.x_max = scale_axis(x_max, old_xmax, old_xmin, width, 0)
        self.y_min = scale_axis(y_min, old_ymax, old_ymin, height, 0)
        self.y_max = scale_axis(y_max, old_ymax, old_ymin, height, 0)
        
        self.a = (float(width) * 6 / 8) / (clicks['br'][0] -  clicks['tl'][0])
        self.c = ((float(width) / 8) - (self.a *  clicks['tl'][0])) / float(width)
        self.e = (float(height) * 6 / 8) / (clicks['br'][1] - clicks['tl'][1])
        self.f = ((float(height) / 8) - (self.e * clicks['tl'][1])) / float(height)

        self.libinput_values = XInputCalibrationMatrix.compute(self.blocks, width, height, clicks)

    def calibrar_ejes(self):
        """
        Guarda una nueva referencia de los ejes.
        """
        
        self.__escalar_ejes()
        try:
            if FAKE_DEV:
                return

            XInput.set_prop(self.device, '"libinput Calibration Matrix"',
                            "{:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f}".format(
                                self.libinput_values[0],
                                self.libinput_values[1],
                                self.libinput_values[2],
                                self.libinput_values[3],
                                self.libinput_values[4],
                                self.libinput_values[5],
                                self.libinput_values[6],
                                self.libinput_values[7],
                                self.libinput_values[8]
                            ))
        except Exception as e:
            logger.exception(e)
            logger.error('Comandos de calibración no fueron ejecutados.')