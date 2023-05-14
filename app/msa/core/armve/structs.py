struct_tag_header = Struct("tag_header",
                           UBInt8("token"),
                           UBInt8("tipo_tag"),
                           UBInt16("size"))
struct_tag = Struct("tag",
                    Embed(struct_tag_header),
                    Bytes("crc32", 4),
                    Bytes("timestamp", 4),
                    Bytes("user_data", lambda ctx: ctx.size))