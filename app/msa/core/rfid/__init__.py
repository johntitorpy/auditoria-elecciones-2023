from msa.core.rfid.constants import CANT_BLOQUES, COD_TIPOS_NXP, COD_TIPOS_ST, MAX_SIZE


def get_tag_type(serial):
    """ Obtiene el tipo de tag según el serial del chip utilizando los bits
        37 y 36 del serial.
    """
    """
    # Obtengo el serial en bits
    int_serial = int.from_bytes(serial, byteorder="big")
    bit_serial = bin(int_serial)

    # Limpio el 0b del inicio
    bit_serial = bit_serial[2:]

    # Calculo el tipo, obteniendo los bits (64-x) donde x es 36 y 37
    tipo = bit_serial[64 - 37: 64 - 35]
    """
    MASK_BIT_NXP = 0b00011000
    # Cargo los campos con los valores obtenidos del serial
    uid_type = serial[0]
    uid_manufacturer = serial[1]
    uid_ic_model = serial[2]
    uid_icode_model = serial[3]

    # compruebo que el tipo de Tag sera ISO15693
    if uid_type != 0XE0:
        print("falla comprobacion EO")
        return None

    # Chequeo que sean de las marcar permitidas actualmente (ST or NXP)
    if uid_manufacturer == 0x02:
        print("DETECCION ST")
        return COD_TIPOS_ST.get(uid_ic_model)
    elif uid_manufacturer == 0x04:
        # Hago una mascara con el valor para obtener los bits 36,37
        print("DETECCION NXP")
        uid_icode_model = (uid_icode_model & MASK_BIT_NXP)
        return COD_TIPOS_NXP.get(uid_icode_model)

    print("Falla deteccion FINAL")

    return None

def get_tag_n_blocks(serial):
    """ Obtiene la cantidad de bloques disponibles para un modelo de tag.
    """
    modelo_tag = get_tag_type(serial)
    return CANT_BLOQUES.get(modelo_tag)


def get_max_payload_size(serial):
    modelo_tag = get_tag_type(serial)
    return MAX_SIZE[modelo_tag]
