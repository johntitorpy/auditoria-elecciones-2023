#!/usr/bin/env python3
from msa.modulos import get_sesion
from msa.modulos.calibrador import Modulo
from msa.modulos.constants import MODULO_CALIBRADOR


def main():
    """Corre el módulo calibrador solamente."""
    get_sesion(iniciar_hw=False, force=True)

    modulo = Modulo(MODULO_CALIBRADOR)
    modulo.main()


if __name__ == '__main__':
    main()
