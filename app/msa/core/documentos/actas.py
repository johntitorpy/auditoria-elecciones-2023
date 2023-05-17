from struct import pack as struct_pack

from base64 import b64encode
from binascii import hexlify, unhexlify
from codecs import encode, decode
from io import BytesIO
from os import urandom
import math
import unicodedata
from zlib import crc32
import struct
import six

from construct import Container
from msa.constants import CAM_BOL_CONT, CAM_TOT_VOT
from msa.core.config_manager import Config
from msa.core.crypto import encriptar, desencriptar
from msa.core.data import Ubicacion
from msa.core.data.candidaturas import Candidatura, Categoria, Lista
from msa.core.data.constants import TIPO_DOC
from msa.core.data.helpers import get_config
from msa.core.documentos.autoridades import Autoridad
from msa.core.documentos.constants import (BITS_DNI, CIERRE_CERTIFICADO,
                                           CIERRE_COPIA_FIEL,
                                           CIERRE_ESCRUTINIO, CIERRE_RECUENTO,
                                           CIERRE_TRANSMISION, CIERRE_TACHAS,
                                           CIERRE_PREFERENCIAS)
from msa.core.documentos.helpers import (decodear_string_apertura,
                                         encodear_string_apertura,
                                         smart_title)
from msa.core.documentos.settings import GUARDAR_DNI, QR_TEXTUAL, SPLIT_NP_PAYLOAD
from msa.core.documentos.structs import (struct_apertura, struct_recuento,
                                         struct_recuento_dni)
from msa.core.crypto.structs import struct_recuento_control, struct_timestamp
from msa.core.documentos.tabulacion import Pizarra
from msa.core.exceptions import (MesaNoEncontrada, QRMalformado,
                                 SerialRepetido, TagMalformado, TipoQrErroneo)
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.imaging.acta import ImagenActa
from msa.core.imaging.qr import crear_qr
from msa.core.logging import get_logger
from msa.core.packing.settings import SMART_PACKING
from msa.core.rfid.constants import TAG_PRUEBA_CTX, TAG_RECUENTO, TAG_NO_ENTRA, MAX_SIZE, TIPO_NXP_SLIX2
from msa.core.settings import TOKEN
from six.moves import range, zip

logger = get_logger("core_documentos_actas")


from msa.core.packing import smart_numpacker
from msa.core.packing import numpacker

from msa.core.packing.numpacker import pack_slow, unpack_slow
import importlib


class BadTagSecuence(Exception):
    pass

class Acta():

    clase_acta = "ACTA"                     # prefijo para QR y serialización

    def _encode_qr(self, qr):
        output = BytesIO()
        qr.save(output, format='PNG')
        qr_img_data = output.getvalue()
        output.close()
        header = 'data:image/png;base64,'
        qr_data = header + b64encode(qr_img_data).decode()
        return qr_data


class Apertura(Acta):

    """Apertura de mesa de votacion."""

    def __init__(self, mesa, autoridades=None, hora=None):
        if autoridades is None:
            autoridades = []
        self.autoridades = autoridades

        self.mesa = mesa
        self.hora = hora or {'horas': 8, 'minutos': 0}

    def a_tag(self, compacto=False):
        """Devuelve la informacion del apertura para almacenar en tag rfid."""
        # "compactamos" si son muchas autoridades de mesa (casos especiales)
        cant_autoridades = len(self.autoridades)
        if not compacto or cant_autoridades <= 2:
            compactar = 0                   # guardar todo
        elif cant_autoridades <= 4:
            compactar = 1                   # no guardar nombre
        else:
            compactar = 2                   # no guardar ni nombre ni apellido
        # guarda los campos indicados (apellido/nombre) de las autoridades
        # hasta el limite disponible, según prioridad (por orden, DNI siempre)
        for max_autoridades in range(cant_autoridades + 1, 0, -1):
            nombres, dnis, tipos = self.encodear_autoridades(compactar,
                                                             max_autoridades)
            container = Container(numero_mesa=int(self.mesa.id_unico_mesa),
                                  hora=int(self.hora["horas"]),
                                  minutos=int(self.hora["minutos"]),
                                  cantidad_autoridades=len(self.autoridades),
                                  len_nombres=len(nombres),
                                  nombres=nombres,
                                  tipos=tipos,
                                  dnis=dnis,
                                  len_docs=len(dnis)
                                  )
            built = struct_apertura.build(container)
            # calcular bits a ocupar vs disponibles:
            if not compactar or len(built) * 8 <= smart_numpacker.MAXBITS:
                break

        return built

    def encodear_autoridades(self, compactar=0, max_autoridades=None):
        # para "compactar" usar 0: todo, 1: sin nombre, 2 sin nombre/apellido
        # max_autoridades limita la cantidad de campos (nombre/apellidos)
        # el DNI se guarda siempre
        if max_autoridades is None:
            max_autoridades = len(self.autoridades)
        nombres = []
        dnis = []
        tipos = []
        for pos, autoridad in enumerate(self.autoridades):
            if compactar < 2 and pos < max_autoridades:
                nombres.append(autoridad.apellido)
            else:
                nombres.append("")
            if compactar < 1 and pos < max_autoridades:
                nombres.append(autoridad.nombre)
            else:
                nombres.append("")
            tipo = "%s" % TIPO_DOC.index(autoridad.tipo_documento)
            tipos.append(tipo.encode())
            dnis.append(int(autoridad.nro_documento))

        nombres = encodear_string_apertura(";".join(nombres))
        dnis = pack_slow(dnis, BITS_DNI)
        return nombres, dnis, tipos

    @classmethod
    def desde_tag(cls, tag):
        """Devuelve un apertura a partir de la informacion de un tag rfid."""
        # parseamos los datos del tag.
        datos = struct_apertura.parse(tag)
        # instanciamos una mesa
        mesa = Ubicacion.first(id_unico_mesa=str(datos.numero_mesa))
        # extraemos los nombres y DNIs
        nombres = decodear_string_apertura(datos.nombres).split(";")
        dnis = unpack_slow(datos.dnis, BITS_DNI)
        # y armamos las autoridades
        autoridades = []
        for i in range(datos.cantidad_autoridades):
            apellido = nombres.pop(0)
            nombre = nombres.pop(0)
            tipo = datos.tipos.pop(0)
            dni = dnis.pop(0)
            autoridad = Autoridad(apellido, nombre, tipo, dni)
            autoridades.append(autoridad)
        # armamos el diccionario de la hora
        hora = {
            "horas": datos.hora,
            "minutos": datos.minutos
        }
        # y finalmente instanciamos la Apertura que vamos a devolver
        apertura = Apertura(mesa, autoridades, hora)
        return apertura

    @forzar_idioma(DEFAULT_LOCALE)
    def a_imagen(self, mostrar=None, svg=False):
        """Devuelve la imagen para imprimir el apertura."""
        if mostrar is None:
            mostrar = {
                "en_pantalla": False
            }
        mostrar["texto"] = mostrar.get("texto", True)

        clase_imagen_acta = self.get_instancia_imagen()
        imagen = clase_imagen_acta(self, mostrar)
        rendered = imagen.render(svg)
        return rendered

    def get_instancia_imagen(self):
        config = Config(["imaging"], self.mesa.codigo)
        actas = config.val("imagenes_actas")
        return getattr(
            importlib.import_module("msa.core.imaging.actas"), actas["apertura"]
        )

    def a_qr_str(self):
        """Devuelve la informacion del recuento para almacenar en qr."""
        datos = [self.mesa.numero,
                 "%s:%s" % (self.hora["horas"], self.hora["minutos"])]
        for autoridad in self.autoridades:
            dato = ",".join((autoridad.apellido, autoridad.nombre,
                             str(autoridad.nro_documento)))
            datos.append(dato)
        return ";".join(datos)

    def a_qr(self):
        datos = self.a_qr_str()
        return crear_qr(datos)

    def a_qr_b64_encoded(self):
        qr_data = None
        qr = self.a_qr()
        if qr is not None:
            qr_data = self._encode_qr(qr)
        return qr_data

    def __str__(self):
        return 'Apertura de ' + self.mesa.descripcion


class Recuento(Acta):

    """Recuento de votos de una mesa."""

    # usar la configuración predeterminada para empaquetamiento de numeros:
    smart_packing = SMART_PACKING
    clase_acta = "REC "                     # prefijo para QR y serialización
    tipo_tag = TAG_RECUENTO                 # código para identificar el tag
    len_serial = 8                          # longitud del número de serie

    def __init__(self, mesa: Ubicacion, autoridades=None, hora=None):

        if autoridades is None:
            autoridades = []

        self.autoridades = autoridades
        self.mesa = mesa
        self.grupo_cat = None

        self.hora = hora  # si hora es None no se muestra el texto del acta
        _campos_extra = get_config("campos_extra")
        self.campos_extra = dict(list(zip(_campos_extra,
                                          [0] * len(_campos_extra))))
        _lst_esp = self.mesa.listas_especiales
        if _lst_esp is not None:
            dict_esp = dict(list(zip(_lst_esp, [0] * len(_lst_esp))))
        else:
            dict_esp = {}
        self.listas_especiales = dict_esp

        self.reiniciar_resultados()

    def actualizar_lista_especial(self, key, votos, suma_al_total=True):
        if suma_al_total:
            valor_actual = self.listas_especiales[key]
            self.campos_extra[CAM_TOT_VOT] += votos - valor_actual

        self.listas_especiales[key] = votos
        self.invalidar_control()

    def serial_sumado(self, serial):
        """Determina si un serial ya ha sido sumado en el recuento."""
        return serial in self._serials

    def sumar_seleccion(self, seleccion, serial=None):
        """Suma una seleccion a los resultados."""
        if seleccion is not None:
            if serial is None or not self.serial_sumado(serial):
                self.pizarra.sumar_seleccion(seleccion)
                if serial is not None:
                    self._serials.append(serial)
                self.campos_extra[CAM_BOL_CONT] += 1
                self.campos_extra[CAM_TOT_VOT] += 1
                self.invalidar_control()
            else:
                raise SerialRepetido()
        else:
            raise ValueError("La seleccion es Invalida")

    def boletas_contadas(self):
        """Obtiene la cantidad de selecciones contadas."""
        return self.campos_extra[CAM_BOL_CONT]

    def total_boletas(self):
        return self.campos_extra[CAM_TOT_VOT]

    def reiniciar_resultados(self):
        """Reinicia los resultados del recuento."""
        self.pizarra = Pizarra()

        self._serials = []
        self.campos_extra[CAM_BOL_CONT] = 0
        self.campos_extra[CAM_TOT_VOT] = 0
        self.invalidar_control()

    def invalidar_control(self):
        """Limpiar código de control y serial utilizado para el checksum"""
        # recalcular el "checksum" criptográfico (cuando se grabe el chip):
        self.cod_control = None
        self.serial = None

    def get_resultados(self, id_umv=None):
        """Devuelve todos los resultados o uno en especifico."""
        # si le pedimos uno solo busca los votos de ese candidato.
        if id_umv is not None:
            ret = self.pizarra.votos_candidato(id_umv)
        else:
            # Sino devolvemos todos
            votos = self.pizarra.get_votos_actuales()
            # Si el acta está desglosada devolvemos la categorias que tiene el
            # acta guardada
            if self.grupo_cat is not None:
                categorias_grupo = Categoria.many(id_grupo=self.grupo_cat)
                cods_categoria = [cat.codigo for cat in categorias_grupo]
                ret = {}
                for key in votos.keys():
                    cand = Candidatura.one(id_umv=key,
                                           cod_categoria__in=cods_categoria)
                    if cand is not None:
                        ret[key] = votos[key]
            else:
                # no esta desglosada devolvemos todos los votos.
                ret = votos
        return ret

    def get_tachas(self, id_umv=None, nro_orden=None):
        return self.pizarra.tachas_candidato(id_umv, nro_orden)

    def get_preferencias(self, cod_categoria, id_umv=None):
        return self.pizarra.preferencias_candidato(cod_categoria, id_umv=id_umv)

    def get_all_preferencias_agrupadas_por_principal(self):
        return self.pizarra.get_all_preferencias_agrupadas_por_principal()

    def get_preferencias_agrupadas_por_principal(self, cod_categoria):
        return self.pizarra.get_preferencias_agrupadas_por_principal(cod_categoria)

    def get_extra_data(self, tipo_acta, serializar_dni=True):
        """Genera la data extra para mandarle al servicio de impresion."""
        if self.autoridades:
            autoridades = [aut.a_dict() for aut in self.autoridades]
        else:
            autoridades = None

        extra_data = {
            "tipo_acta": tipo_acta,
            "autoridades": autoridades,
            "hora": self.hora,
            "clase_acta": self.clase_acta,
            "con_dni": serializar_dni,
            "serial": self.serial,
        }
        return extra_data

    def a_tag(self, grupo_cat=None, con_dnis=GUARDAR_DNI, cant_dni_max=None,
              aes_key=None, serial=None, free_chip_mem=smart_numpacker.MAXBITS):
        """Devuelve la informacion del recuento para almacenar en tag rfid."""

        # armar lista con los datos a serializar:
        valores = []

        tachas = self.get_tachas()

        candidatos = Candidatura.para_recuento(grupo_cat)
        for candidato in candidatos:
            if (candidato.categoria.posee_tachas and not candidato.es_blanco):
                    if candidato in Candidatura.candidatos_principales():
                        tachas_candidato = tachas.get(candidato.id_umv)
                        for nro_orden, cantidad in tachas_candidato.items():
                            valores.append(cantidad)
            elif (candidato.categoria.posee_preferencias and not candidato.es_blanco):
                cantidad = self.get_preferencias(candidato.cod_categoria, candidato.id_umv)
                valores.append(cantidad)
            else:
                resultado = self.get_resultados(candidato.id_umv)
                valores.append(resultado)
        ordered_keys = sorted(self.campos_extra.keys())
        for key in ordered_keys:
            valores.append(self.campos_extra[key])

        ordered_keys = sorted(self.listas_especiales.keys())
        for key in ordered_keys:
            valores.append(self.listas_especiales[key])

        # inicializar un contenedor con los datos mínimos para calcular tamaño:
        container = Container()
        container.grupo = int(grupo_cat) if grupo_cat is not None else 0
        container.datos = b""
        substruct_map = dict([(struct.name, struct) for struct
                               in struct_recuento_control.subcons])
        # código de control inicial vacio, y timestamp:
        container.cod_control = b"\x00" * substruct_map["cod_control"].sizeof()
        container.update(self.timestamp)

        if con_dnis:
            struct = struct_recuento_dni
            documentos = []
            # almacenar DNI de autoridades de mesa, mínimo 2 (empaquetados):
            for autoridad in self.autoridades[:cant_dni_max]:
                documentos.append(int(autoridad.nro_documento))
            documentos = pack_slow(documentos, BITS_DNI)
            container.len_docs = len(documentos)
            container.documentos = documentos
        else:
            struct = struct_recuento

        # empaquetar la lista de valores, según el algorítmo que corresponda:
        num_mesa = self.mesa.id_unico_mesa
        if self.smart_packing:
            # calcular bits libres disponibles:
            free_chip_mem = free_chip_mem - len(struct.build(container)) * 8
            # intentar armar una serialización compacta, si no es posible
            # levanta la restricción de tamaño ("modo especial QR ilimitado")
            for bits in (free_chip_mem, None):
                try:
                    datos = smart_numpacker.pack(int(num_mesa), valores,
                                                 max_bits=bits)
                except OverflowError:
                    continue
                else:
                    break
            container.datos = datos
            # intentar quitar un DNI para poder guardar los datos (recursivo):
            if len(datos) * 8 > free_chip_mem and cant_dni_max is not None:
                if cant_dni_max:
                    cant_dni_max -= 1
                    return self.a_tag(grupo_cat, con_dnis, cant_dni_max,
                                      aes_key=aes_key, serial=serial)
        else:
            # redondear a bytes el campo nro de mesa:
            n = math.ceil(smart_numpacker.BITS_NUMERO_MESA / 8)
            cod_mesa = int(num_mesa).to_bytes(n, "big")
            # intentar empaquetar con la menor cantidad de bits por valor:
            for bits in range(9, numpacker.CANTIDAD_BITS_PACKER):
                try:
                    packed = numpacker.pack(valores, bits)
                    break
                except:
                    continue
            else:
                # no debería suceder (lanzo excepción por sanidad):
                raise RuntimeError("No se pudo empaquetar, incrementar const.")
            # armar string de bytes:
            datos = cod_mesa + int(bits).to_bytes(1, "big") + packed
            container.datos = datos

        if serial is not None:
            self.serial = serial
        elif aes_key:
            self.invalidar_control()

        # crear un "checksum" criptográfico (a.k.a. código de control)
        # el vector de inicialización es implicito (ver propiedad/método)
        if aes_key:
            gcm_tag, null = encriptar(aes_key, self.init_vector, b"", datos,
                                      tag_size=len(container.cod_control))
            self.cod_control = gcm_tag
        if self.cod_control:
            container.cod_control = self.cod_control

        return struct.build(container)

    def a_qr_str(self, grupo_cat=None, con_dnis=True, textual=QR_TEXTUAL,
                 tipo_acta=None):
        """Devuelve la informacion del recuento para almacenar en qr."""
        if not textual:
            # empaquetar datos binarios:
            encoded_data = self.a_tag(grupo_cat, con_dnis, free_chip_mem=2464*20)
            serial = decode(self.serial, "hex_codec")
            datos = bytearray(b"")
            # Agregamos el Token
            datos.append(int(TOKEN, 16))
            
            # Agregamos el crc32
            int_crc = crc32(encoded_data)
            
            # Formateamos el CRC32 en el mismo formato que viene del tag
            crc_datos = struct.pack("I", int_crc)
            datos.extend(crc_datos)

            # agregamos el largo de los datos en 2 bytes
            len_data = len(encoded_data + serial) * 2
            datos.extend(struct_pack(">H", len_data))
            # metemos el resto de los datos
            datos.extend(encoded_data)
            # agregamos el número de serie:
            datos.extend(serial)
            # lo encodeamos en hexa y lo pasamos a mayúsculas
            todo = encode(datos, "hex_codec").decode().upper()
            return todo
        else:
            # armar datos en texto (no binario) para codificar en el QR:
            datos = [self.mesa.descripcion_completa]
            # recorrer categorias (cargos principales):
            candidatos = Candidatura.para_recuento(grupo_cat)
            candidatos_principales = Candidatura.candidatos_principales()
            for candidato in candidatos:
                if candidato.categoria.adhiere is None:
                    cod_cargo = candidato.codigo
                    if candidato in candidatos_principales or candidato.es_blanco:
                        votos = self.get_resultados(candidato.id_umv)
                        if candidato.lista:
                            lista = candidato.lista.nombre
                        else:
                            lista = candidato.codigo
                        datos += ["%s: %s" % (lista, votos)]
            # listas espceciales y campos extra:
            datos += ["%s: %s" % (key, self.listas_especiales[key])
                      for key in self.listas_especiales]
            datos += ["%s: %s" % campo
                      for campo in self.campos_extra.items()]
            datos = ", ".join(datos)
            # normalizo los acentos, y convertir a ASCII plano "7 bits"
            datos = unicodedata.normalize('NFKD', datos)
            datos = datos.encode("ASCII", "ignore").decode("ASCII", "ignore")
            return datos

    def a_qr(self, grupo_cat=None, con_dnis=True, tipo_acta=None):
        datos = self.clase_acta + self.a_qr_str(grupo_cat, con_dnis,
                                                tipo_acta=tipo_acta)
        return crear_qr(datos)

    def a_qr_b64_encoded(self, grupo_cat=None, tipo_acta=None):
        qr_data = None
        qr = self.a_qr(grupo_cat, tipo_acta=tipo_acta)
        if qr is not None:
            qr_data = self._encode_qr(qr)
        return qr_data

    def generar_titulo(self, tipo):
        # Por defecto no tenemos titulo, a menos que el tipo de acta tenga
        # titulo.
        titulo = ""
        leyenda = None
        # Muestra el icono del verificador en la boleta. Si no tiene chip en el
        # documento en el que imprimimos no imprimirmos el verificador.
        verif = True

        # Internamente todas las actas son iguales, lo que cambia es el texto
        # que se imprime, pero el acta una vez serializada no sabe cual es.
        if tipo == CIERRE_RECUENTO:
            # El acta de cierre.
            titulo = _("titulo_recuento")
            leyenda = _("no_insertar_en_urna")
            verif = False
        elif tipo == CIERRE_TACHAS:
            # El acta de cierre.
            titulo = _("titulo_recuento_tachas")
            leyenda = _("no_insertar_en_urna")
        elif tipo == CIERRE_PREFERENCIAS:
            # El acta de cierre.
            titulo = _("titulo_recuento_preferencias")
            leyenda = _("no_insertar_en_urna")
        elif tipo == CIERRE_TRANSMISION:
            # El acta de transmision.
            titulo = _("titulo_transmision")
            leyenda = _("no_insertar_en_urna")
        elif tipo in (CIERRE_CERTIFICADO, CIERRE_ESCRUTINIO):
            # El certificado de escrutinio.
            titulo = _("titulo_certificado")
            verif = False
        elif tipo == CIERRE_COPIA_FIEL:
            # Una copia fiel del certificado. (Certificado sin datos desc_mesa
            # autoridades)
            titulo = _("titulo_copia_fiel")
            verif = False

        return titulo, leyenda, verif


    @forzar_idioma(DEFAULT_LOCALE)
    def a_imagen(self, mostrar=None, tipo=None, svg=False):
        """Devuelve la imagen para imprimir recuento.

        Argumentos:
        tipo -- una tupla con el tipo de acta y el id_de grupo de categorias.
            Puede ser None si no no queremos agrupar.
        mostrar -- un diccionario con las cosas a mostrar.
        svg -- Devuelve un svg si True, en caso contrario un objeto PIL.Image
        """
        if mostrar is None:
            mostrar = {
                "en_pantalla": False
            }

        if tipo is None:
            tipo = (CIERRE_RECUENTO, None)

        titulo, leyenda, verif = self.generar_titulo(tipo[0])
        tipo_acta = tipo[0]

        mesa = self.mesa
        # Armamos los datos para el texto.
        datos = {
            'tipo': tipo[0],
            'titulo': titulo,
            'autoridades': self.autoridades,
            'mesa': mesa,
            'hora': self.hora,
            'leyenda': leyenda,
            'cod_datos': self.mesa.cod_datos,
        }

        if self.hora is not None:
            datos["horas"] = "%02d" % self.hora.get('horas', "")
            datos["minutos"] = "%02d" % self.hora.get('minutos', "")
            mostrar["texto"] = True
        else:
            datos["horas"] = ""
            datos["minutos"] = ""
            mostrar["texto"] = False

        mostrar["verificador"] = verif

        clase_imagen_acta = self.get_instancia_imagen(mesa)
        imagen = clase_imagen_acta(self, tipo_acta, mostrar, datos)

        rendered = imagen.render(svg)

        # Devolvemos la imagen en el formato solicitado.
        return rendered


    def get_instancia_imagen(self, mesa):
        posee_preferencias = Categoria.one(id_grupo=self.grupo_cat, preferente=True)
        config = Config(["imaging"], mesa.codigo)

        actas = config.val("imagenes_actas")
        if posee_preferencias is not None:
            nombre_clase_imagen_acta = actas["recuento_con_preferencia"]
        else:
            nombre_clase_imagen_acta = actas["recuento_sin_preferencia"]

        return getattr(importlib.import_module("msa.core.imaging.actas"), 
                            nombre_clase_imagen_acta)

    def __str__(self):
        """Representacion como string del acta."""
        return 'Recuento de la mesa %s' % self.mesa

    @classmethod
    def desde_tag(cls, tag, con_dnis=GUARDAR_DNI, aes_key=None, serial=None):
        # Si vamos a guardar los dnis usamos el struct con DNIS, sino no.
        if con_dnis:
            struct = struct_recuento_dni
        else:
            struct = struct_recuento
        # Parseamos el tag
        datos_tag = struct.parse(tag)

        # Nos fijamos si el tag tiene la data de una categoria o solo de una
        if cls.smart_packing:
            try:
                string_datos = b""
                for byte in datos_tag.datos:
                    string_datos += byte
                num_mesa, valores = smart_numpacker.unpack(string_datos)
            except IndexError as e:
                raise TagMalformado(e)
        else:
            tag = b""
            for byte in datos_tag.datos:
                tag += byte
            n = math.ceil(smart_numpacker.BITS_NUMERO_MESA / 8)
            num_mesa = int.from_bytes(tag[:n], "big")
            # extraigo los campos empaquetados y los desempaqueto:
            bits = tag[n]
            packed = tag[n + 1:]
            valores = numpacker.unpack(packed, bits)

        mesa = Ubicacion.first(id_unico_mesa=str(num_mesa))
        if not mesa:
            raise MesaNoEncontrada()
        mesa.usar_cod_datos()
        recuento = cls(mesa)
        grupo = datos_tag.grupo
        # Establecemos el grupo del recuento, si viene en 0 lo establecemos en
        # None
        recuento.grupo_cat = grupo if grupo else None

        # armamos el diccionario de la hora (timestamp)
        recuento.hora = {
            "horas": datos_tag.horas,
            "minutos": datos_tag.minutos,
            "segundos": datos_tag.segundos,
        }
        recuento.serial = serial

        # Traemos las candidaturas que se guardaron en el recuento
        candidatos = Candidatura.para_recuento(recuento.grupo_cat)
        for candidato in candidatos:
            if candidato.categoria.posee_tachas and not candidato.es_blanco:
                cant_tachas = len(Candidatura.tachas(id_umv=candidato.id_umv))
                votos = []
                for i in range(cant_tachas):
                    votos.append(valores.pop(0))

                for i, voto in enumerate(votos):
                    recuento.pizarra.set_tacha_candidato(
                        candidato.id_umv, i+1, voto)

                recuento.pizarra.set_votos_candidato(candidato.id_umv, sum(votos))
            elif (candidato.categoria.posee_preferencias and not candidato.es_blanco):
                votos = valores.pop(0)
                recuento.pizarra.set_preferencia_candidato(candidato.categoria.codigo,
                    candidato.id_umv, votos)

                recuento.pizarra._sumar_votos_candidato(candidato.principal.id_umv, votos)
            else:
                recuento.pizarra.set_votos_candidato(candidato.id_umv, valores.pop(0))

        # extraemos los campos extras (boletas_contadas, total_boletas, etc)
        ordered_keys = sorted(recuento.campos_extra.keys())
        for key in ordered_keys:
            recuento.campos_extra[key] = valores.pop(0)

        # extraemos las listas especiales (OBS, IMP, NUL, REC, etc)
        ordered_keys = sorted(recuento.listas_especiales.keys())
        for key in ordered_keys:
            recuento.listas_especiales[key] = valores.pop(0)

        # si estan los DNIS los extraemos del tag
        if con_dnis:
            documentos = unpack_slow(datos_tag.documentos, BITS_DNI)
            len_documentos = len(documentos)
            for dni in documentos:
                autoridad = Autoridad("", "", 0, dni)
                recuento.autoridades.append(autoridad)

        # verificar el checksum criptográfico (lanza excepción)
        if aes_key:
            gcm_tag = datos_tag.cod_control
            desencriptar(aes_key, recuento.init_vector, gcm_tag, b"",
                         b"".join(datos_tag.datos), tag_size=len(gcm_tag))

        # preservar el "checksum" criptográfico (código de control) para el QR
        recuento.cod_control = datos_tag.cod_control

        return recuento

    @classmethod
    def desde_qr(cls, datos):
        """Devuelve un recuento a partir de la informacion de un qr."""
        # tipo de qr
        if datos.startswith(cls.clase_acta):
            datos = datos[4:]

        token = datos[0:2]
        if token != TOKEN:
            raise TipoQrErroneo()

        crc32_data = datos[2:10]
        
        len_datos = int(datos[10:14], 16)
        datos_recuento = datos[14:-cls.len_serial*2]
        serial = datos[-cls.len_serial*2:]
        if len_datos != len(datos_recuento + serial):
            raise QRMalformado()

        bytes_recuento = bytearray(b'')
        for i in range(0, len(datos_recuento), 2):
            bytes_recuento.append(int(datos_recuento[i:i+2], 16))

        if unhexlify(crc32_data) != struct.pack("I",crc32(bytes_recuento)):
            raise QRMalformado('El crc32 no coincide')

        recuento = cls.desde_tag(bytes_recuento, con_dnis=True, serial=serial)

        return recuento

    @classmethod
    def desde_dict(cls, id_planilla, hora, data_dict, campos_extra):
        """Genera un recuento desde un diccionario con los datos.
           Argumentos:
            id_planilla -- el id_planilla del acta que queremos generar.
            hora -- un diccionario con la hora {"horas": int, "minutos": int}
            data_dict -- un diccionario con los datos. De key el id_ubicacion y
                de value la cantidad de votos.
            listas_especiales -- un diccionaio con las listas_especiales
                de key el id_de lista especial y de value un diccionario que a
                su vez tiene de key el codigo de categoria y la cantidad de
                votos especiales como valor.
            campos_extra -- un diccionario con los campos_extra como key y el
                valor numerico del campo extra como valor.
        """
        mesa = Ubicacion.one(id_planilla=id_planilla)
        mesa.usar_cod_datos()
        recuento = cls(mesa, hora=hora)
        for key, value in data_dict.items():
            recuento.pizarra.set_votos_candidato(key, value)
        recuento.campos_extra = campos_extra
        return recuento

    def a_human(self):
        texto = "{} - {}, {}, {} ({})\n".format(self.mesa.descripcion,
                                                self.mesa.escuela,
                                                self.mesa.municipio,
                                                self.mesa.departamento,
                                                self.mesa.codigo)
        for autoridad in self.autoridades:
            texto += "Autoridad: {}\n".format(autoridad.nro_documento)

        grupo = int(self.grupo_cat) if self.grupo_cat is not None else 1
        for categoria in Categoria.many(sorted="posicion",
                                        id_grupo=grupo):
            texto += "{}\n".format(categoria.nombre)
            for lista in Lista.many(sorted='codigo'):
                candidato = Candidatura.one(cod_categoria=categoria.codigo,
                                            cod_lista=lista.codigo)
                if candidato is not None:
                    votos = self.get_resultados(candidato.id_umv)
                    texto += "\t{} - {} Votos: {}\n".format(lista.nombre,
                                                            candidato.nombre,
                                                            votos)
            candidato = Candidatura.one(cod_categoria=categoria.codigo,
                                        clase="Blanco")
            if candidato is not None:
                votos = self.get_resultados(candidato.id_umv)
                texto += "\t{}: {}\n".format(_("votos_en_blanco"), votos)
            texto += "\n"

        texto += "\nCampos extra:\n"
        ordered_keys = sorted(self.campos_extra.keys())
        for key in ordered_keys:
            texto += "{}: {}\n".format(key, self.campos_extra[key])

        texto += "\nListas Especiales:\n"
        ordered_keys = sorted(self.listas_especiales.keys())
        for key in ordered_keys:
            titulo = _("titulo_votos_{}".format(key))
            texto += "{}: {}\n".format(titulo, self.listas_especiales[key])

        return texto

    @property
    def init_vector(self):
        """Vector de inicialización utilizado para generar el checksum"""
        container = Container()
        container.update(self.timestamp)
        timestamp = struct_timestamp.build(container)
        id_mesa = int(self.mesa.id_unico_mesa) if int(self.mesa.id_unico_mesa) < 65500 else 65500
        iv = b"".join([
            int(id_mesa).to_bytes(2, "big"),
            timestamp,
            decode(self.serial, "hex_codec")[-(self.len_serial-1):],
            ])
        assert len(iv) == 12
        return iv

    @property
    def timestamp(self):
        """Marca de tiempo del recuento (horas, minutos, segundos)"""
        # rellenar campos faltantes
        timestamp = self.hora or {}
        for substruct in struct_timestamp.subcon.subcons:
            if not substruct.name in timestamp:
                timestamp[substruct.name] = 0
        return timestamp

    @property
    def serial(self):
        """Numero de serie del recuento"""
        # devuelve convertido a representación en hexadecimal
        if not self._serial:
            # generar nro serie aleatorio provisional (especialmente testing):
            self._serial = b"\x00" + urandom(self.len_serial - 1)
        return hexlify(self._serial).decode()

    @serial.setter
    def serial(self, uid):
        # internamente se maneja en bytes para evitar problemas de comparación
        self._serial = unhexlify(uid) if uid else None

class PruebaCTX(Acta):
    """Clase que implementa las actas de prueba de conexión. Toma la estructura de un recuento
    con dnis dando la posibilidad en un futuro a agregarle otro contenido de forma sencilla, 
    ademas de facilitar la integración con TREP.

    El nro_ctx por ahora queda fijo en 0 y no se usa. Siempre existe la posibilidad de poder 
    pasar este valor en el constructor y se va a guardar numpackeado como se guarda el nro de mesa
    en el recuento.

    Args:
        Acta ([type]): [description]

    Raises:
        RuntimeError: [description]

    Returns:
        [type]: [description]
    """

    # usar la configuración predeterminada para empaquetamiento de numeros:
    smart_packing = SMART_PACKING
    clase_acta = "CTX "                     # prefijo para QR y serialización
    tipo_tag = TAG_PRUEBA_CTX               # código para identificar el tag
    len_serial = 8                          # longitud del número de serie

    def __init__(self, contenido=[0,0,0,0,0,0,0,0], nro_ctx=0):
        self._contenido = contenido
        self._nro_ctx = nro_ctx
        self.hora = None

    def a_tag(self, free_chip_mem=smart_numpacker.MAXBITS):
        """Devuelve la informacion del recuento para almacenar en tag rfid."""

        # armar lista con los datos a serializar:
        valores = self._contenido

        # inicializar un contenedor con los datos mínimos para calcular tamaño:
        container = Container()
        container.grupo = 0
        container.datos = b""
        substruct_map = dict([(struct.name, struct) for struct
                               in struct_recuento_control.subcons])
        # código de control inicial vacio, y timestamp:
        container.cod_control = b"\x00" * substruct_map["cod_control"].sizeof()

        struct = struct_recuento_dni

        container.len_docs = 0
        container.documentos = pack_slow([], BITS_DNI)
        container.update(self.timestamp)

        if self.smart_packing:
            # calcular bits libres disponibles:
            if not SPLIT_NP_PAYLOAD:
                free_chip_mem = free_chip_mem - len(struct.build(container)) * 8
            
            # intentar armar una serialización compacta, si no es posible
            # levanta la restricción de tamaño ("modo especial QR ilimitado")
            for bits in (free_chip_mem, None):
                try:
                    datos = smart_numpacker.pack(self._nro_ctx, valores,
                                                 max_bits=bits)                    
                except OverflowError:
                    continue
                else:
                    break
            container.datos = datos
        else:
            # redondear a bytes el campo nro de mesa:
            n = math.ceil(smart_numpacker.BITS_NUMERO_MESA / 8)
            cod_mesa = int(self._nro_ctx).to_bytes(n, "big")
            # intentar empaquetar con la menor cantidad de bits por valor:
            for bits in range(9, numpacker.CANTIDAD_BITS_PACKER):
                try:
                    packed = numpacker.pack(valores, bits)
                    break
                except:
                    continue
            else:
                # no debería suceder (lanzo excepción por sanidad):
                raise RuntimeError("No se pudo empaquetar, incrementar const.")
            # armar string de bytes:
            datos = cod_mesa + int(bits).to_bytes(1, "big") + packed
            container.datos = datos

        return struct.build(container)

    @classmethod
    def desde_tag(cls, tag):
        
        # Parseamos el tag
        datos_tag = struct_recuento_dni.parse(tag)
        if cls.smart_packing:
            try:

                string_datos = b""
                for byte in datos_tag.datos:
                    string_datos += byte
                nro_ctx, valores = smart_numpacker.unpack(string_datos)
            except IndexError as e:
                raise TagMalformado(e)
        else:
            tag = b""
            for byte in datos_tag.datos:
                tag += byte
            n = math.ceil(smart_numpacker.BITS_NUMERO_MESA / 8)
            nro_ctx = int.from_bytes(tag[:n], "big")
            # extraigo los campos empaquetados y los desempaqueto:
            bits = tag[n]
            packed = tag[n + 1:]
            valores = numpacker.unpack(packed, bits)

        prueba_ctx = cls(contenido=valores, nro_ctx=nro_ctx)
        
        prueba_ctx.hora = {
                "horas": datos_tag.horas,
                "minutos": datos_tag.minutos,
                "segundos": datos_tag.segundos,
            }

        return prueba_ctx


    def a_qr_str(self):
        """Devuelve la informacion del recuento para almacenar en qr."""
        # empaquetar datos binarios:
        encoded_data = self.a_tag(free_chip_mem=2464*6)
        
        datos = bytearray(b"")
        # Agregamos el Token
        datos.append(int(TOKEN, 16))
        
        # Agregamos el crc32
        int_crc = crc32(encoded_data)
        
        # Formateamos el CRC32 en el mismo formato que viene del tag
        crc_datos = struct.pack("I", int_crc)
        datos.extend(crc_datos)

        # agregamos el largo de los datos en 2 bytes
        len_data = len(encoded_data) * 2
        datos.extend(struct_pack(">H", len_data))
        # metemos el resto de los datos
        datos.extend(encoded_data)
        
        # lo encodeamos en hexa y lo pasamos a mayúsculas
        todo = encode(datos, "hex_codec").decode().upper()
        return todo
    
    def a_qr(self):
        datos = self.clase_acta + self.a_qr_str()
        return crear_qr(datos)

    @classmethod
    def desde_qr(cls, datos):
        """Devuelve un recuento a partir de la informacion de un qr."""
        # tipo de qr
        if datos.startswith(cls.clase_acta):
            datos = datos[4:]

        token = datos[0:2]
        if token != TOKEN:
            raise TipoQrErroneo()

        crc32_data = datos[2:10]
        
        len_datos = int(datos[10:14], 16)
        datos_recuento = datos[14:]
        
        if len_datos != len(datos_recuento):
            raise QRMalformado()

        bytes_recuento = bytearray(b'')
        for i in range(0, len(datos_recuento), 2):
            bytes_recuento.append(int(datos_recuento[i:i+2], 16))

        if unhexlify(crc32_data) != struct.pack("I",crc32(bytes_recuento)):
            raise QRMalformado('El crc32 no coincide')

        recuento = cls.desde_tag(bytes_recuento)

        return recuento

    def a_qr_b64_encoded(self):
        qr_data = None
        qr = self.a_qr()
        if qr is not None:
            qr_data = self._encode_qr(qr)
        return qr_data
    
    @forzar_idioma(DEFAULT_LOCALE)
    def a_imagen(self, svg=False):
        """Devuelve la imagen para el acta de prueba de CTX."""

        # Se importa en este punto para no generar referencias
        # circulares.
        from msa.core.imaging.actas import ImagenActaCTX

        imagen = ImagenActaCTX(self)

        rendered = imagen.render(svg)

        # Devolvemos la imagen en el formato solicitado.
        return rendered
    
    @property
    def timestamp(self):
        """Marca de tiempo del recuento (horas, minutos, segundos)"""
        # rellenar campos faltantes
        timestamp = self.hora or {}
        for substruct in struct_timestamp.subcon.subcons:
            if not substruct.name in timestamp:
                timestamp[substruct.name] = 0
        return timestamp


class Totalizacion(Recuento):

    """Suma de recuentos de votos de varias mesa."""

    # usar siempre num_packer para empaquetamiento de numeros grandes:
    smart_packing = False
    clase_acta = "TOT "                     # prefijo para QR y serialización
    tipo_tag = TAG_NO_ENTRA                 # código para diferenciar el tag

    def __init__(self, mesa, autoridades=None, hora=None):
        super().__init__(mesa, autoridades, hora)

    def sumar_recuento(self, recuento, serial):
        if not serial or not self.serial_sumado(serial):
            resultados = recuento.get_resultados()

            for key, votos in resultados.items():
                actual = self.get_resultados(key)
                self.pizarra.set_votos_candidato(key, actual + votos)

            for key, votos in six.iteritems(recuento.campos_extra):
                actual = self.campos_extra.get(key, 0)
                self.campos_extra[key] = actual + votos

            for key, votos in six.iteritems(recuento.listas_especiales):
                actual = self.listas_especiales.get(key, 0)
                self.listas_especiales[key] = actual + votos

            if serial:
                self._serials.append(serial)
        else:
            raise SerialRepetido()

    def generar_titulo(self, tipo):
        titulo = _("titulo_totalizacion")
        leyenda = None
        verif = True
        return titulo, leyenda, verif
