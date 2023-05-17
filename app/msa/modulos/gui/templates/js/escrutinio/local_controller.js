/**
 * @namespace js.escrutinio.local_controller
 */

// chancleta.js
/* global Chancleta */

// base.js
/* global ocultar_loader */

/**
 * Genera una estructura para acceder facilmente al nro_orden a partir del id_umv
 */
function generar_tabla_id_umv_nro_orden(candidaturas){
    let id_umv_nro_orden = {};
    candidaturas.forEach(candidatura => {
        id_umv_nro_orden[candidatura.id_umv] = candidatura.nro_orden;
    });
    return id_umv_nro_orden;
}

/**
 * Devuelve el nro_orden a partir del id_umv
 * 
 * @param {*} id_umv 
 * @returns 
 */
function get_nro_orden(id_umv){
    return local_data.id_umv_nro_orden[id_umv];
}

var local_data = {};

/**
 * Recibe los datos del backend y los tranforma en objetos de Chancleta
 * para poder manipularlos como si fueran objetos de Ojota.
 * Oculta el loader.
 * @param {*} data - Datos del backend.
 */
function cargar_datos(data) {
    local_data.categorias = new Chancleta(data.categorias);
    local_data.candidaturas = new Chancleta(data.candidaturas);
    local_data.agrupaciones = new Chancleta(data.agrupaciones);
    local_data.id_umv_nro_orden = generar_tabla_id_umv_nro_orden(data.candidaturas);

    var candidatos = local_data.candidaturas.many({ clase: "Candidato" });

    for (var i in candidatos) {
        var candidato = candidatos[i];
        if (candidato.cod_lista) {
            candidato.lista = get_lista_candidato(candidato);
        }
        if (candidato.cod_partido) {
            candidato.partido = get_partido_candidato(candidato);
        }
        if (candidato.cod_alianza) {
            candidato.alianza = get_alianza_candidato(candidato);
        }
        candidato.categorias_hijas = get_categorias_hijas_candidato(candidato);
    }
    ocultar_loader();
}

/**
 * Devuelve el objeto lista de un candidato.
 *
 * @param {*} candidato - El candidato requerido.
 */
function get_lista_candidato(candidato) {
    return local_data.agrupaciones.one({ id_candidatura: candidato.cod_lista });
}

/**
 * Devuelve el objeto partido de un candidato.
 *
 * @param {*} candidato - El candidato requerido.
 */
function get_partido_candidato(candidato) {
    return local_data.agrupaciones.one({
        id_candidatura: candidato.cod_partido,
    });
}

/**
 * Devuelve el objeto alianza de un candidato.
 *
 * @param {*} candidato - El candidato requerido.
 */
function get_alianza_candidato(candidato) {
    return local_data.agrupaciones.one({
        id_candidatura: candidato.cod_alianza,
    });
}

/**
 * Devuelve las categorias hijas de un candidato.
 *
 * @param {*} candidato - El candidato requerido.
 */
function get_categorias_hijas_candidato(candidato) {
    var ret = [];

    // Obtenemos las categorias hijas de la categoría del candidato.
    var categorias_hijas = local_data.categorias.many({
        adhiere: candidato.cod_categoria,
    });

    if (categorias_hijas.length) {
        // Recorremos las categorias hijas buscando un candidato de esta lista.
        for (var j in categorias_hijas) {
            var categoria = categorias_hijas[j];
            if (categoria) {
                const candidato_hijo = local_data.candidaturas.one({
                    cod_categoria: categoria.codigo,
                    cod_lista: candidato.cod_lista,
                });
                // Si existe tal candidato lo agregamos a la lista de
                // candidatos hijos.
                if (candidato_hijo) {
                    var cat_hija = [
                        categoria.codigo,
                        candidato_hijo,
                        categoria,
                    ];
                    ret.push(cat_hija);
                }
            }
        }
    }
    return ret;
}

function en_seleccion(seleccion, candidato) {
    for (let i in seleccion) {
        id_umv = seleccion[i];

        if (id_umv.constructor === Array) {
            if (id_umv.includes(candidato.id_umv)) return true;
        } else {
            if (candidato.id_umv == id_umv) return true;
        }
    }
    return false;
}

/**
* Devuelve las preferencias buscando por lista y cargo
* Copy paste de sufragio
*
* @param {*} candidato
*/
function get_preferencias(cod_lista, cod_categoria){
    var filter = {
        clase: "Candidato",
        cod_lista: cod_lista,
        cod_categoria: cod_categoria,
        sorted: "nro_orden"
    };
    return local_data.candidaturas.many(filter);
}

function get_candidato_principal(candidato){
    var filter = {
        clase: "Candidato",
        cod_lista: candidato.cod_lista,
        cod_categoria: candidato.cod_categoria,
        sorted: "nro_orden"
    };
    return local_data.candidaturas.first(filter);
}

/* exported local_data */
/* exported cargar_datos */
