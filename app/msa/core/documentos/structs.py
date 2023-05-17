from construct import (Array, Bytes, Embed, GreedyRange, Struct, UBInt8,
                       UBInt16, OptionalGreedyRange)
from msa.core.documentos.constants import LEN_LEN_OPC, LEN_LEN_UBIC
from msa.core.crypto.structs import struct_recuento_control


struct_voto = Struct(
    "voto",
    Bytes("len_ubic", LEN_LEN_UBIC),
    Bytes("ubicacion", lambda ctx: int(ctx.len_ubic)),
    Bytes("len_opciones", LEN_LEN_OPC),
    Array(lambda ctx: int(ctx.len_opciones), UBInt16("opciones")),
    Bytes("len_tachas", LEN_LEN_OPC),
    Array(lambda ctx: int(ctx.len_tachas), UBInt16("tachas")),
    Bytes("len_preferencias", LEN_LEN_OPC),
    Array(lambda ctx: int(ctx.len_preferencias), UBInt16("preferencias"))
)

struct_recuento = Struct(
    "Recuento",
    Embed(struct_recuento_control),
    UBInt8("grupo"),
    OptionalGreedyRange(Bytes("datos", 1))
)

struct_recuento_dni = Struct(
    "Recuento con dni",
    UBInt8("len_docs"),
    Bytes("documentos", lambda ctx: ctx.len_docs),
    Embed(struct_recuento),
)

struct_apertura = Struct(
    "Apertura",
    UBInt16("numero_mesa"), UBInt8("hora"), UBInt8("minutos"),
    UBInt8("cantidad_autoridades"), UBInt8("len_nombres"),
    Array(lambda ctx: ctx.len_nombres, Bytes("nombres", 1)),
    Array(lambda ctx: ctx.cantidad_autoridades, Bytes("tipos", 1)),
    UBInt8("len_docs"),
    Bytes("dnis", lambda ctx: ctx.len_docs),
)
