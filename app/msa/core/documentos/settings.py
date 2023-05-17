ACTA_DESGLOSADA = False

# Cantidad de suplentes ademas del presidente en las autoridades de mesa
CANTIDAD_SUPLENTES = 1

# (No) Almacenar DNI en acta de Recuento:
GUARDAR_DNI = True

# No Empaquetar resultados en el Recuento (sólo impresión, ignorado en tests):
QR_TEXTUAL = False

#: Indica si se permite dividir los datos generados por numpacker en N actas hasta que se logre guardar todos los bytes.
SPLIT_NP_PAYLOAD = False

try:
    from msa.core.documentos.settings_local import *
except ImportError:
    pass
