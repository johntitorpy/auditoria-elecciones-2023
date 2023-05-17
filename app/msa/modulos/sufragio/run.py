#!/usr/bin/env python3
"""Punto de entrada al sistema. Establece cuales son los modulos de inicio y cuales son los que estarán habilitados.
"""
from msa.modulos.base.disk_runner import DiskRunner
from msa.modulos.constants import MODULO_INICIO
from msa.modulos.sufragio.constants import MODULOS_APLICACION
from msa.core.logging import get_logger


def main():
    """Funcion de entrada del sistema de la BUE. Establece los modulos de inicio y los habilitados al crear una instancia
    de :meth:`DiskRunner <modulos.base.disk_runner.DiskRunner>` y pasarlos como parámetros al constructor.
    Corre el sistema ejecutando :meth:`DiskRunner.run() <modulos.base.disk_runner.DiskRunner.run>`.
    """
    modulos_startup = [MODULO_INICIO]

    runner = DiskRunner(modulos_startup, MODULOS_APLICACION)
    runner.run()


if __name__ == '__main__':
    logger = get_logger("run")
    try:
        main()
    except:
        logger.exception("Excepción en la app principal, finalizando.")
        raise
    else:
        logger.info("Terminando sin excepción")
