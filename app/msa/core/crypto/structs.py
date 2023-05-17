from construct import Struct, Bytes, UBInt8, BitStruct, BitField, Embed
GMAC_TAG_SIZE = 4

# estructura para construir el contenido del tag de un voto.
struct_voto = Struct(
    "voto",
    Bytes("gcm_tag", 16),
    UBInt8("len_datos"),
    Bytes("datos", lambda ctx: ctx.len_datos),
)

# estructura para construir el contenido de la credencial de autoridad de mesa.
struct_credencial = Struct(
    "credencial",
    Bytes("gcm_tag", 16),
    Bytes("salt", 16),
    Bytes("datos", 16),
    Bytes("firma", 48),
)

# estructura para construir el contenido de la credencial de autoridad de mesa.
struct_credencial_turing = Struct(
    "credencial_turing",
    Embed(struct_credencial),
    Bytes("serial", 8),
)

# estructura para construir el contenido de la credencial de tecnico.
struct_credencial_tecnico_turing = Struct(
    "credencial",
    Bytes("gcm_tag", 16),
    Bytes("salt", 16),
    UBInt8("len_datos"),
    Bytes("datos", lambda ctx: ctx.len_datos),
    Bytes("firma", 48),
    Bytes("serial", 8),
)

# estructura para construir el contenido de la credencial de tecnico.
struct_credencial_tecnico = Struct(
    "credencial",
    Bytes("gcm_tag", 16),
    Bytes("salt", 16),
    UBInt8("len_datos"),
    Bytes("datos", lambda ctx: ctx.len_datos),
    Bytes("firma", 48),
)

# marca de tiempo
struct_timestamp = BitStruct("timestamp",
        BitField("horas", 5),
        BitField("minutos", 6),
        BitField("segundos", 13),
    )

# estructura para "checksum" criptográfico en recuento ("código de control")
struct_recuento_control = Struct(
    "control",
    Embed(struct_timestamp),
    Bytes("cod_control", GMAC_TAG_SIZE),                    # gcm_tag
)
