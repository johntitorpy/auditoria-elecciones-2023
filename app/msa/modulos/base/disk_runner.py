from argparse import ArgumentParser

from msa.modulos.base import App
from msa.modulos.constants import MODULO_CALIBRADOR


class DiskRunner:
    """
    Corre la aplicación en el contexto del DVD.

    Attributes:
        app (modulos.base.App): administra la ejecución de los módulos.
        con_calibracion (bool):
            determina si se agrega :const:`modulos.constants.MODULO_CALIBRADOR` a :attr:`modulos_aplicacion`.
        modulos_startup (list[str]):
            módulos de inicio que se den ejecutar primero. Es lo que se va a cargar en
            :attr:`modulos.base.App.modulos_startup`
        modulos_aplicacion (list[str]):
            módulos que serán habilitado para ejecutarse. Es lo que se va a cargar en
            :attr:`modulos.base.App.modulos_habilitados`
    """

    def __init__(self, modulos_startup, modulos_aplicacion, calibracion=True):
        """Establece módulos de inicio y de aplicación.

        Argumentos:
            modulos_startup (list[str]): los módulos a ejecutar al inicio.
            modulos_aplicacion (list[str]) los módulos de la aplicación.
        """
        self.app = None
        self.con_calibracion = calibracion

        self.modulos_startup = modulos_startup
        self.modulos_aplicacion = modulos_aplicacion
        if calibracion:
            self.modulos_aplicacion.append(MODULO_CALIBRADOR)
        self.init_parser()

    def init_parser(self):
        """Inicializa el parseador de argumentos."""
        self.parser = ArgumentParser("run.py")
        self.set_args()
        self.parse_args()

    def set_args(self):
        """Establece los argumentos aceptados por el parser."""
        if self.con_calibracion:
            self.parser.add_argument(
                '-c', '--calibrar', action='store_true', default=False,
                help="Ejecuta el modulo de calibracion en primera instancia.")

    def parse_args(self):
        """Parsea los argumentos y actúa en consecuencia."""
        args = self.parser.parse_args()

        if self.con_calibracion and args.calibrar:
            self.modulos_startup.append(MODULO_CALIBRADOR)

        return args

    def init_app(self):
        """Inicializa la aplicación. Crea una instancia de :meth:`modulos.base.App <modulos.base.App>` con los módulos
        de inicio y módulos de aplicación (módulos habilitados)

        .. todo::
            Este método es innecesario. Esta línea podría ir en :meth:`run`.

        """
        self.app = App(self.modulos_startup, self.modulos_aplicacion)

    def run(self):
        """Llama a :meth:`App.run() <modulos.base.App.run>`."""
        self.init_app()
        self.app.run()
