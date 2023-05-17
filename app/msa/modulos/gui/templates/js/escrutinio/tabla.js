/**
 * @namespace js.escrutinio.tabla
 */

// escrutinio/ipc.js
/* global constants */

// escrutinio/local_controller.js
/* global local_data */

// handlebars.js
/* global Handlebars */

// helpers.js
/* global fetch_template */
/* global ordenar_absolutamente */

// Cache para la tabla.
var _tabla_inicial = null;
// Cache para los titulos de la tabla.
var _titulos = null;

/**
 * Genera la tabla con los datos de las candidaturas.
 * @param {*} data - Data con los datos de las candidaturas.
 */
function generar_tabla_inicial(data) {
    var filas = [];
    var filter = { adhiere: null };
    if (data.grupo_cat !== null) {
        filter.id_grupo = data.grupo_cat;
    }
    // Filtro todas las categorias del grupo que quiero mostrar.
    var categorias = local_data.categorias.many(filter);
    var agrupaciones = local_data.agrupaciones.many();
    agrupaciones = agrupaciones.sort(ordenar_absolutamente);

    // shortcuts
    var usa_alianzas = constants.TABLA_MUESTRA_ALIANZA;
    var usa_partidos = constants.TABLA_MUESTRA_PARTIDO;

    // recorro las agrupaciones para armar la tabla
    for (var i in agrupaciones) {
        var agrupacion = agrupaciones[i];
        var fila = null;

        if (agrupacion.clase == "Alianza") {
            // resistir la tentación de juntar estos ifs. si los juntamos va a
            // entrar en el else y no queremos eso.
            if (usa_alianzas) {
                // si es una alianza y mostramos alianzas en la tabla.
                fila = _generar_alianza(agrupacion);
            }
        } else if (agrupacion.clase == "Partido") {
            // resistir la tentación de juntar estos ifs. si los juntamos va a
            // entrar en el else y no queremos eso.
            if (usa_partidos) {
                // si es un partido y usamos partidos en la tabla.
                fila = _generar_partido(agrupacion);
            }
        } else {
            // las listas aparecen siempre.
            fila = _generar_lista(agrupacion, categorias);
        }

        // si esta agrupacion se agrega como fila la agregamos.
        if (fila != null) {
            filas.push(fila);
        }
    }
    // agregamos la fila de voto en blanco si hay voto en blanco para alguna de
    // las categorias
    var fila_blanco = _generar_lista_blanca(categorias);
    if (fila_blanco.categorias.length) {
        filas.push(fila_blanco);
    }

    _tabla_inicial = filas;
}

/**
 * Genera la fila de partido.
 *
 * @param {*} partido - Partido a mostrar en la tabla.
 */
function _generar_partido(partido) {
    var fila = {
        tipo: "partido",
        datos: partido,
        expande: true,
    };
    fila.descripcion = partido.nombre;
    return fila;
}

/**
 * Genera la fila de Alianza.
 *
 * @param {*} alianza - Alianza a mostrar en la tabla.
 */
function _generar_alianza(alianza) {
    var fila = {
        tipo: "alianza",
        datos: alianza,
        expande: true,
    };
    fila.descripcion = alianza.nombre;
    return fila;
}

/**
 * Carga el template de Handlebars de los colores.
 * @param {*} colores - Los colores a mostrar en pantalla.
 */
const crear_div_colores_helper = (template) => (colores) => {
    var item = "";
    if (colores) {
        var template_data = {
            num_colores: colores.length,
            colores: colores,
        };
        item = template(template_data);
    }
    return new Handlebars.SafeString(item);
};

/**
 * Genera la fila de la Lista.
 *
 * @param {*} lista - La lista a mostrar en la tabla.
 * @param {*} categorias - Las categorías.
 */
function _generar_lista(lista, categorias) {
    var fila_lista = {
        tipo: "lista",
        datos: lista,
        categorias: [],
        expande: categorias.length == 1, // Si hay una sola categoria, entonces expande
        mostrar_numero_lista: constants.USAR_NUMERO_LISTA,
    };
    // Si mostramos el color generamos el gradiente.
    if (constants.USAR_COLOR) {
        fila_lista.color = lista.color;
    }

    // mostramos el nombre corto o el largo segun la setting
    if (constants.USAR_NOMBRE_CORTO) {
        fila_lista.descripcion = lista.nombre_corto;
    } else {
        fila_lista.descripcion = lista.nombre;
    }

    // Agregamos candidatos para cada categoria, incluso para los espacios
    // vacios
    for (var j in categorias) {
        var categoria = categorias[j];
        var candidato = _generar_candidato(lista, categoria);

        fila_lista.categorias.push(candidato);
    }
    return fila_lista;
}

/**
 * Genera la fila para voto en blanco.
 *
 * @param {*} categorias - Las categorías de los votos en blanco.
 */
function _generar_lista_blanca(categorias) {
    var fila_lista = {
        tipo: "lista",
        datos: { numero: "", codigo: "BLC" },
        categorias: [],
        expande: categorias.length == 1,
        mostrar_numero_lista: constants.USAR_NUMERO_LISTA,
        descripcion: "Votos en Blanco",
        es_blanco: true,
    };

    for (var j in categorias) {
        var categoria = categorias[j];
        var candidato = local_data.candidaturas.one({
            cod_categoria: categoria.codigo,
            id_candidatura: constants.cod_lista_blanco,
        });

        /**FIXME: evitar usar chequeos por undefined y preferir !== por sobre !==*/
        if (typeof candidato != "undefined") {
            fila_lista.categorias.push(candidato);
        }
    }
    return fila_lista;
}

/**
 * Genera el cuadradito para el candidato.
 *
 * @param {*} lista - La lista a mostrar.
 * @param {*} categoria - La categoría.
 */
function _generar_candidato(lista, categoria) {
    var filter = {
        cod_lista: lista.codigo,
        cod_categoria: categoria.codigo,
        sorted: "nro_orden"
    };
    var candidato = local_data.candidaturas.one(filter);
    return candidato;
}

/**
 * Genera las filas para la tabla.
 *
 * @param {*} data - Contiene los datos para generar las filas.
 */
function generar_filas(data) {
    var votos = data.datos_tabla;
    var seleccion = data.seleccion;
    if (_tabla_inicial === null) {
        generar_tabla_inicial(data);
    }
    var filas = _tabla_inicial;

    for (var i in filas) {
        var fila = filas[i];
        for (var j in fila.categorias) {
            var candidato = fila.categorias[j];
            /**FIXME: evitar usar chequeos por undefined y preferir !== por sobre !==*/
            if (typeof candidato != "undefined") {
                candidato.clase_resaltado = "";
                let voto = votos[candidato.id_umv];
                if (typeof voto === "undefined") {
                    voto = "0"; // Este 0 tiene que ser un string para que Handlebars lo vea como "algo" y no como "nada".
                } else {
                    if (typeof seleccion !== "undefined" && seleccion !== null) {
                        categoria = local_data.categorias.one({codigo: candidato.cod_categoria});
                        let _en_seleccion = false;
                        if(categoria.preferente && candidato.clase !=="Blanco"){
                            const preferencias = get_preferencias(
                                candidato.cod_lista,
                                candidato.cod_categoria
                            );
                            _en_seleccion = preferencias.some(
                                preferencia => en_seleccion(data.seleccion, preferencia)
                            );
                        }else{
                            _en_seleccion = en_seleccion(data.seleccion, candidato);
                        }
                        if(_en_seleccion)
                            candidato.clase_resaltado = "resaltado";
                    }
                }
                if (voto === 0) {
                    voto = "0"; // por lo mismo que lo comentado arriba
                }
                candidato.votos = voto;
            }
        }
    }

    return filas;
}

/**
 * Genera las filas especiales para mostrar en la tabla
 * luego de la clasificacion de votos.
 */
function generar_filas_especiales(data) {
    var filas = [];
    var listas_especiales = data.listas_especiales;
    var total_general = data.total_general;
    var orden_especiales = data.orden_especiales;

    //Filas especiales "normales"
    if (listas_especiales !== null) {
        for (var i in orden_especiales) {
            var codigo = orden_especiales[i];
            var votos = listas_especiales[codigo];
            var fila_especial = {
                tipo: "especial",
                id_fila: codigo,
                descripcion: constants.titulos_especiales[codigo],
                votos: votos,
            };
            filas.push(fila_especial);
        }
        // en escrutinio, ocultar cant. boletas si se muestran listas especiales
        if (!constants.totalizador) {
            document.querySelector("#cantidad_escrutadas").style.display =
                "none";
        }
    }
    // Fila total general
    if (total_general !== null) {
        var fila_total = {
            tipo: "total-general",
            id_fila: "total_general",
            descripcion: constants.i18n.total_general,
            votos: total_general,
        };
        filas.push(fila_total);
    }

    return filas;
}

/**
 * Precachea los títulos de la tabla.
 *
 * @param {*} grupo_cat - Grupo a partir del cual filtrar las categorías.
 */
function generar_titulos(grupo_cat) {
    if (_titulos === null) {
        const titulos = ["Listas"];
        const filter = { adhiere: null };
        if (grupo_cat !== null) {
            filter.id_grupo = grupo_cat;
        }
        var categorias = local_data.categorias.many(filter);
        for (var i in categorias) {
            titulos.push(categorias[i].codigo);
        }
        _titulos = titulos;
    }
    return _titulos;
}

/**
 * Genera los botones de scroll para la tabla.
 */
function generar_scroll() {
    const elementHeight = (element) => element.getBoundingClientRect().height;
    const tabla = document.querySelector("#tabla");
    const alto_contenedor = elementHeight(tabla.parentElement);
    const alto_thead = elementHeight(tabla.querySelector("thead"));
    const alto_flechas =
        elementHeight(tabla.querySelector(".contenedor-scroll.arriba")) +
        elementHeight(tabla.querySelector(".contenedor-scroll.abajo"));
    const alto_tabla_regulares = elementHeight(
        tabla.querySelector("tbody.votos-regulares")
    );
    const alto_tabla_especiales = elementHeight(
        tabla.querySelector("tbody.votos-especiales")
    );

    const activarScroll =
        alto_tabla_regulares + alto_tabla_especiales + alto_thead >
        alto_contenedor;

    if (!activarScroll) {
        return displayScroll("none");
    }

    const nuevo_alto_tabla_regulares =
        alto_contenedor - alto_tabla_especiales - alto_flechas - alto_thead;
    tabla.querySelector(
        "tbody.votos-regulares"
    ).style.height = `${nuevo_alto_tabla_regulares}px`;
    bindear_botones_scroll();
}

/**
 * Bindea los botones del scroll.
 */
function bindear_botones_scroll() {
    document
        .getElementById("scroll-arriba")
        .removeEventListener("click", scroll_arriba);
    document
        .getElementById("scroll-abajo")
        .removeEventListener("click", scroll_abajo);
    document
        .getElementById("scroll-arriba")
        .addEventListener("click", scroll_arriba);
    document
        .getElementById("scroll-abajo")
        .addEventListener("click", scroll_abajo);

    //Posicion inicial
    displayScroll("block");

    document
        .querySelector("tbody.contenedor-scroll.arriba")
        .classList.add("deshabilitado");
    document.querySelector("tbody.votos-regulares").scrollTop = 0;

    document
        .querySelector("tbody.votos-regulares")
        .addEventListener("scroll", () => habilitar_botones_scroll());
}

const displayScroll = (display = "block") => {
    Array.from(document.querySelectorAll("tbody.contenedor-scroll")).map(
        (i) => {
            i.style.display = display;
        }
    );
};

/**
 * Habilita los botones de scroll.
 */
function habilitar_botones_scroll() {
    //Si no puedo seguir scrolleando, deshabilita el boton
    const elemento = document.querySelector("tbody.votos-regulares");
    const contenedor_arriba = document.querySelector(
        "tbody.contenedor-scroll.arriba"
    );
    const contenedor_abajo = document.querySelector(
        "tbody.contenedor-scroll.abajo"
    );

    const elemento_height = elemento.getBoundingClientRect().height;
    const habilitar_arriba = elemento.scrollTop !== 0;
    const habilitar_abajo =
        elemento.scrollHeight - elemento.scrollTop !== elemento_height;

    // por default se deshabilitan los botones
    [contenedor_arriba, contenedor_abajo].map((contenedor) =>
        contenedor.classList.add("deshabilitado")
    );
    if (habilitar_arriba) {
        contenedor_arriba.classList.remove("deshabilitado");
    }
    if (habilitar_abajo) {
        contenedor_abajo.classList.remove("deshabilitado");
    }
}

/** Callback del clic del botón, scrollea la tabla hacia arriba. */
function scroll_arriba() {
    var posicion_actual = document.querySelector("tbody.votos-regulares")
        .scrollTop;
    document.querySelector("tbody.votos-regulares").scrollTop =
        posicion_actual - 50;
}

/* Callback del clic del botón, scrollea la tabla hacia abajo. */
function scroll_abajo() {
    var posicion_actual = document.querySelector("tbody.votos-regulares")
        .scrollTop;
    document.querySelector("tbody.votos-regulares").scrollTop =
        posicion_actual + 50;
}

/**
 * Actualiza la tabla con los ultimos datos.
 */
function actualizar_tabla(data) {
    var filter = { adhiere: null };
    if (data.grupo_cat !== null) {
        filter.id_grupo = data.grupo_cat;
    }
    var categorias = local_data.categorias.many(filter);
    var len_categorias = categorias.length;

    const data_template = {};
    data_template.titulos = generar_titulos(data.grupo_cat);
    data_template.filas = generar_filas(data);
    data_template.num_filas = len_categorias + 1;
    data_template.ancho_filas_especiales =
        len_categorias == 1 ? 2 : len_categorias;
    //data_template.ancho_titulo = len_categorias == 1 ? 2 : 1;
    data_template.ancho_titulo = "";
    data_template.filas_especiales = generar_filas_especiales(data);
    renderizar_tabla(data_template);

    if (mostrar_tabla_preferentes()) {
        tablaPreferentes.actualizar(data);
    }

    function mostrar_tabla_preferentes() {
        return hay_preferencias(generar_titulos(data.grupo_cat), data);
    }
}

const renderizar_tabla = (template_data) => {
    fetch_template("tabla", "pantallas/escrutinio").then((template_tabla) => {
        const html_tabla = template_tabla(template_data);
        document.querySelector("#tabla").innerHTML = html_tabla;
        generar_scroll();
        scrollear_a_principal();
    });
};

/**
 * Sube o scrollea la pantalla hacia la pantalla principal.
 */
function scrollear_a_principal() {
    const fila_resaltada = document.querySelector(".resaltado.col_0");
    if (!fila_resaltada) return;
    const fila_resaltada_offset = fila_resaltada.getBoundingClientRect().top;
    document.querySelector("tbody.votos-regulares").scrollTop =
        fila_resaltada_offset - 60;
}

/**
 * Borra los resaltados de la tabla.
 */
function borrar_resaltado() {
    Array.from(document.querySelectorAll("#tabla td")).map((i) =>
        i.classList.remove("resaltado")
    );
}

/**
 * Registra el helper de handlebar de los colores.
 */
function registrar_helper_colores(template_colores) {
    const crear_div_colores = crear_div_colores_helper(template_colores);
    Handlebars.registerHelper("colores", crear_div_colores);
}

/**
 * Construye la url a una imagen de candidatura
 * 
 * @param {String} imagen - nombre de la imagen
 * @returns 
 */
function path_imagen(imagen) {
    var nombre_imagen = imagen + "." + constants.ext_img_voto;
    if (imagen == "BLC") {
        nombre_imagen = "BLC.svg";
    }
    var img_path = "imagenes_candidaturas/" + constants.juego_de_datos + "/";
    var src = img_path + nombre_imagen;
    return src;
}

/**
 * Construye un tag html con la imagen
 * 
 * @param {String} imagen - nombre de la imagen
 * @returns 
 */
function crear_img(imagen) {
    var src = path_imagen(imagen);
    var tag = '<img src="' + src + '" />';
    return new Handlebars.SafeString(tag);
}

/**
 * Registra el helper de handlebar para la imagen de un candidato.
 */
function registrar_helper_imagenes() {
    Handlebars.registerHelper("imagen_candidatura", crear_img);
}

/* exported borrar_resaltado */
/* exported actualizar_tabla */
