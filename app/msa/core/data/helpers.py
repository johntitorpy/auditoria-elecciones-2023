# -*- coding: utf-8 -*-
import json
from msa.constants import PATH_VARS
from msa.core.data.settings import JUEGO_DE_DATOS
import os

_tipo_eleccion = None


def get_config(key):
    """
    Obtiene datos de la configuracion de la eleccion. Devuelve el valor correpondiente a la clave que se pasa como
    parametro

    Args:
        key (str): la clave

    Returns:
        str: el valor
    """
    from msa.core.data import Configuracion
    config = Configuracion.one(key)

    if config is not None:
        config = config.valor

    return config

def get_codigos(mesa):
    path_codigos = os.path.join(PATH_VARS,'datos',JUEGO_DE_DATOS,'codigos.json')
    if os.path.exists(path_codigos):
        with open(path_codigos) as json_file:
            codigos = json.load(json_file)
            if mesa in codigos:
                return codigos[mesa]['seguridad']
    return {}

def get_ctx(mesa):
    path_codigos = os.path.join(PATH_VARS,'datos',JUEGO_DE_DATOS,'codigos.json')
    if os.path.exists(path_codigos):
        with open(path_codigos) as json_file:
            codigos = json.load(json_file)
            if mesa in codigos:
                return codigos[mesa]['ctx']
    return {}