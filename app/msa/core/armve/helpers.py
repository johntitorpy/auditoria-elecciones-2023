# coding:utf-8
from __future__ import absolute_import
import os.path
import pyudev
import sys

from binascii import unhexlify
from six.moves import range

from msa.core.armve.settings import SERIAL_PORT


py_version = sys.version_info[0]


def tohex(int_value):
    """Convierte integers a string en formato hex."""
    data_ = format(int_value, 'x')
    result = data_.rjust(6, '0')
    hexed = unhexlify(result)
    return hexed


def array_to_printable_string(array, separator=''):
    """ Convierte un array de ints a un string imprimible con el separador
        que se le pase como parámetro.
        Por ejemplo, en el campo serial de un tag:
        'serial': [224, 4, 1, 0, 126, 33, 9, 63] -> 'e00401007e21093f'
    """
    return separator.join('%02x'.upper() % c for c in array)


def serial_16_to_8(serial):
    return [int(''.join(serial[i:i + 2]), 16) for i in range(0, len(serial),
                                                             2)]


def array_to_string(array):
    """Convierte un array de int a un string."""
    ret = "".join([chr(char) for char in array])
    return ret


def string_to_array(string_):
    """Convierte un sting a un array de int"""
    try:
        print([ord(char) for char in string_])
        array = [ord(char) for char in string_]
    except TypeError:
        print("error", string_)
        array = string_

    return array


def get_arm_port():
    def find_attribute(device, attribute, value):
        try:
            _value = device.attributes.asstring(attribute)
            if _value == value:
                return True
            else:
                return False
        except KeyError:
            _parent = device.parent
            if _parent is not None:
                return find_attribute(_parent, attribute, value)
            else:
                return False
        except Exception as e:
            print("Ocurrió una excepción: {}".format(e))

    def find_msa_device(device, attribute, value):
        if find_attribute(device, attribute, value):
            return device

    port = None
    context = pyudev.Context()
    devices = [device for device in context.list_devices(subsystem='tty')]
    msa_devices = [
        device for device in devices
        if find_msa_device(device, "manufacturer", "MSA S.A.") is not None]

    if len(msa_devices):
        port = msa_devices[0].device_node

    # Fallback, trato de levantar sin pyudev la constante SERIAL_PORT
    if port is None and os.path.exists(SERIAL_PORT):
        print("No se encontró ningún dispositivo, se utiliza {}".format(
            SERIAL_PORT))
        port = SERIAL_PORT

    return port


def is_armve_capable():
    return get_arm_port() is not None
