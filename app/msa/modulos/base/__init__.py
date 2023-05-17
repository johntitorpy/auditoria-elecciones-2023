"""
Modulo base.

Contiene:
    - La aplicacion principal :meth:`App` que corre la maquina la cual se ocupa de correr
      los diferentes modulos.
    - Las clases base para Controladores, Modulos, Rampa y Actions
"""
import gc
import os
from importlib import import_module

from msa.core.audio.player import AudioPlayer
from msa.core.audio.settings import VOLUMEN_GENERAL
from msa.core.i18n import levantar_locales
from msa.core.logging import get_logger
from msa.modulos.constants import (
    COMANDO_APAGADO,
    COMANDO_EXPULSION_CD,
    MODULO_APERTURA,
    MODULO_CALIBRADOR,
    MODULO_INICIO,
    MODULO_TOTALIZADOR,
    MODULO_PRUEBA_EQUIPO,
    SHUTDOWN,
    SUBMODULO_DATOS_APERTURA,
)


class App:
    """
    Es la encargada de correr los diferentes módulos del sistema.

    Attributes:
        modulos_startup (List[str]):
            Los modulos que corren previos a la ejecucion normal de la app.
        modulos_habilitados (List(str)):
            Modulos habilitados para su ejecución.

    """

    def __init__(self, modulos_startup, modulos_habilitados):
        """
        Constructor de la aplicacion. Se deben pasar como parámetros los modulos de inicio y los habilitados. Estos
        deben ser algunos de los modulos establecidos en :ref:`modulos.constants.mods_y_submods`.

        Arguments:
            modulos_startup (List[str]):
                Modulos a correr previo a la ejecucion normal de la app.
            modulos_habilitados (List[str]):
                Modulos a habilitar.
        """
        self.set_locales()
        self.set_volume()
        self.modulos_startup = modulos_startup
        self.modulos_habilitados = modulos_habilitados

    def set_locales(self):
        """Establece los locales de la aplicacion."""
        levantar_locales()

    def set_volume(self):
        """Setea el volumen del audio al nivel deseado antes de iniciar."""
        audioplayer = AudioPlayer(as_daemon=False)
        audioplayer.set_volume(VOLUMEN_GENERAL)
        audioplayer.close()

    def _get_modulo_startup(self):
        """
        Desencola el proximo modulo de inicio y lo devuelve

        Returns:
            str: nombre del modulo
        """
        return self.modulos_startup.pop()

    def apagar_maquina(self):
        """Expulsa el DVD y apaga la maquina."""
        os.system(COMANDO_EXPULSION_CD)
        os.system(COMANDO_APAGADO)

    def _loop(self, modulo=None, titulo=None):
        """Ejecuta la secuencia de modulos de la aplicacion hasta que el valor de retorno de un módulo
        sea :const:`SHUTDOWN <modulos.constants.SHUTDOWN>` o se lanze alguna exception. Cada módulo a ejecutar debe retornar el próximo módulo.
        Primero se ejecutan todos los modulos de inicio (:attr:`modulos_startup`).

        .. todo::
            Mejorar la forma en que se entra en modulo totalizador.
        """

        if modulo is None:
            modulo = self._get_modulo_startup()
        else:
            self.modulos_startup = []

        ejecutar = True
        res = ""
        while ejecutar:
            if modulo in self.modulos_habilitados:
                res = self.ejecutar_modulo(modulo, titulo)

                if len(self.modulos_startup):
                    # Si todavía tengo modulos startup para ejecutar, los ejecuto
                    modulo = self._get_modulo_startup()
                # Si no vengo de un calibrador y el retorno es volver a inicio,
                # o apagar, salgo
                elif modulo not in (
                    MODULO_CALIBRADOR,
                    MODULO_PRUEBA_EQUIPO,
                ) and res in (MODULO_INICIO, SHUTDOWN):
                    # Si no vengo de un calibrador y el retorno es volver a inicio,
                    # o apagar, salgo
                    ejecutar = False
                elif res in self.modulos_habilitados:
                    # Si el valor de retorno corresponde a un modulo ejecutado lo establezco para su ejecución
                    # en la proxima iteración.
                    modulo = res
                elif (
                    res == SUBMODULO_DATOS_APERTURA
                    and MODULO_APERTURA not in self.modulos_habilitados
                ):
                    # para el disco totalizador.
                    # TODO: Habria que resolver mejor esto via disk_runner
                    modulo = MODULO_TOTALIZADOR

                if res == SHUTDOWN:
                    self.apagar_maquina()
            else:
                raise Exception("El modulo {} no existe".format(modulo))

    def _get_clase_modulo(self, modulo):
        """
        Devuelve la clase del modulo.

        Args:
            modulo (str): nombre del modulo

        Returns:
            class: la clase asociada al nombre del modulo.
        """
        if "," in modulo:
            nombre_paquete, submodulo = modulo.split(",")
        else:
            nombre_paquete = modulo
        paquete = import_module(".%s" % nombre_paquete, "msa.modulos")
        clase_modulo = getattr(paquete, "Modulo")
        return clase_modulo

    def ejecutar_modulo(self, modulo, titulo=None):
        """
        Ejecuta un modulo de la aplicacion por su método ``main()`` y le establece su título.

        Args:
            modulo (str): nombre del modulo
            titulo (str): título a establecer en la pantalla del módulo

        Returns:
            str: valor de retorno del módulo ejecutado.
        """

        # Instancio una clase, y ejecuto su metodo main()
        # Este metodo debe devolver un string si quiere llamar a otro modulo
        clase_modulo = self._get_clase_modulo(modulo)
        mod = clase_modulo(modulo)
        res = mod.main(titulo=titulo)

        # Borro explicitamente el modulo de la memoria
        del mod
        # Y ya que estoy llamo al Garbage Collector
        gc.collect()

        return res

    def run(self, modulo=None, titulo=None):
        """Ejecuta el loop de la aplicacion (:meth:`_loop <_loop>`) y captura las excepciones."""
        logger = get_logger("modulos_base")
        try:
            self._loop(modulo, titulo)
        except KeyboardInterrupt:
            pass
        except:
            logger.exception("Excepción en el módulo, finalizando.")
            raise
        else:
            logger.info("Terminando sin excepción")
