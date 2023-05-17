/**
 * @namespace js.escrutinio.base
 */

// escrutinio/tiles.js
/* global slides_asistente */
/* global pantallas */
/* global contexto */

// escrutinio/ipc.js
/* global constants */
/* global load_ready_msg */

// escrutinio/recuento.js
/* global click_secuencia */
/* global actualizar_boleta */
/* global pantalla_boleta_error */
/* global pantalla_boleta_repetida */
/* global pantalla_verificar_acta */
/* global pantalla_inicial */
/* global actualizar_boletas_procesadas */

// escrutinio/asistida.js
/* global salir */

// escrutinio/tabla.js
/* global borrar_resaltado */
/* global actualizar_tabla */

// escrutinio/impresion.js
/* global pantalla_copias */

// patio.js
/* global Patio */

// eventos.js
/* global preparar_eventos */

// zaguan.js
/* global send */

// helpers.js
/* global ready */

var patio = null;

/**
 * Crea el objeto Patio si no fue ya creado.
 * @returns {Promise}
 */
function load_patio() {
    if (patio !== null) {
        return Promise.resolve();
    }
    for (var i in slides_asistente) {
        slides_asistente[i].slide_index = i;
        pantallas.push(slides_asistente[i]);
    }
    patio = new Patio(
        document.querySelector("#contenedor_datos"),
        pantallas,
        contexto,
        "pantallas/escrutinio"
    );
    return new Promise((resolve, reject) => {
        patio
            .load()
            .then(() => {
                document
                    .querySelector("#panel_derecho")
                    .addEventListener("click", click_secuencia);
                document
                    .querySelector("#panel_copias")
                    .addEventListener("click", salir_a_reimpresion);
                resolve();
            })
            .catch((error) => reject(error));
    });


    function salir_a_reimpresion(){
        send("salir_a_reimpresion")
    }
}

/**
 * Carga el CSS del flavor.
 */
function load_css(flavor) {
    var elem = document.createElement('link');
    elem.rel = 'stylesheet';
    elem.href =
        constants.PATH_TEMPLATES_FLAVORS + flavor + '/escrutinio/flavor.css';
    document.getElementsByTagName('head')[0].appendChild(elem);
}

/**
 * Carga las extensiones js del flavor.
 */
function load_extension_js(flavor) {
    return new Promise((resolve) => {
        const extensiones_js = [
            "template-" + flavor + ".js",
            "tiles-" + flavor + ".js"
        ];
        const promises_extensiones_js = extensiones_js.map(
            (file) => load_js(constants.PATH_EXTENSION_JS_MODULO + "/" + file)
        );
        Promise.allSettled(promises_extensiones_js).then(() => {
            resolve();
        });
    });
}

/**
 * Corre esta funcion cuando el documento terminó de cargar.
 */
ready(() => {
    preparar_eventos();
    document.addEventListener("dragstart", (event) => {
        event.target.click();
    });
    load_ready_msg();
});

/**
 * Oculta el loader y envía al back-end el mensaje ``inicializar_interfaz``.
 */
function ocultar_loader() {
    setTimeout(function () {
        send("inicializar_interfaz");
    }, 300);
}

/**
 * Popula el HTML del encabezado de la pagina.
 */
const popular_encabezado = (template_header) => {
    const html_header = template_header({escrutinio: true, mesa: true, mostrar_ubicacion: constants.mostrar_ubicacion});
    document.querySelector("#encabezado").innerHTML = html_header;
};

/**
 * Actualiza la pantalla segun el evento recibido del back-end.
 *
 * @param {*} data - Data recibida del back-end.
 */
function actualizar(data) {
    var tipo_act = constants.tipo_act;
    borrar_resaltado();

    patio.pantalla_boleta_error.hide();
    patio.pantalla_boleta_repetida.hide();
    patio.pantalla_boleta.hide();

    if (data.tipo == tipo_act.ACT_BOLETA_NUEVA) {
        actualizar_boleta(data);
    } else if (data.tipo == tipo_act.ACT_ERROR) {
        setTimeout(pantalla_boleta_error, 200);
    } else if (data.tipo == tipo_act.ACT_BOLETA_REPETIDA) {
        function _repetida() {
            pantalla_boleta_repetida(data);
        }

        setTimeout(_repetida, 200);
    } else if (data.tipo == tipo_act.ACT_VERIFICAR_ACTA) {
        function _repetida() {
            pantalla_verificar_acta(data);
        }

        setTimeout(_repetida, 200);
    } else if (data.tipo == tipo_act.ACT_INICIAL) {
        if (data.reimpresion) {
            pantalla_copias(data.reimpresion_acta, data.qr_reimpresion);
        } else {
            pantalla_inicial();
        }
        if (constants.totalizador) {
            var elem = document.getElementsByTagName("body")[0];
            elem.setAttribute("data-modo", "totalizador");
        }
        actualizar_tabla(data);
        actualizar_boletas_procesadas(data.boletas_procesadas);
    } else if (data.tipo == tipo_act.ACT_ESPECIALES) {
        actualizar_tabla(data);
    }
}

/**
 * Devuelve el valor de la clave "key".
 *
 * @param {*} key - Clave del diccionario "constants.i18n".
 */
function _i18n(key) {
    return constants.i18n[key];
}

/** Helper de handlebars para generar constantes "i18n" */
function registrar_helper_i18n() {
    Handlebars.registerHelper("i18n", _i18n);
}

/* exported patio */
/* exported load_patio */
/* exported ocultar_loader */
/* exported popular_encabezado */
/* exported actualizar */
