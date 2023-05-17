#!/usr/bin/env python3
"""Script de inicio del sistema.

Corre los modulos, maneja la calibracion, la navegacion entre modulos y el
Apagado de la maquina.
"""

from msa.modulos.base.disk_runner import DiskRunner


def main():
    """Funcion de entrada de la aplicacion. Bienvenidos."""
    # esta constante esta aca para que no entre en el disco de votación
    MODULO_PRUEBA_EQUIPO = "prueba_equipo"
    modulos_startup = [MODULO_PRUEBA_EQUIPO]
    modulos_aplicacion = [MODULO_PRUEBA_EQUIPO]

    runner = DiskRunner(modulos_startup, modulos_aplicacion)
    runner.run()


if __name__ == "__main__":
    main()
