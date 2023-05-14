struct_tag_header = Struct("tag_header",
                           UBInt8("token"),
                           UBInt8("tipo_tag"),
                           Bytes("timestamp", 4),
                           UBInt16("size"))
struct_tag = Struct("tag",
                    Embed(struct_tag_header),
                    Bytes("crc32", 4),
                    Bytes("user_data", lambda ctx: ctx.size))