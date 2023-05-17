/**
 * @namespace js.apertura.funciones
 *
 */
/**
 * Funciones del módulo de Apertura.
 */
"use strict";

/**
  * document_ready corre cuando termina de cargar la pagina
  
*/
ready(() => {
    // hookeamos los eventos
    preparar_eventos();
    // y le avisamos al backend que ya terminamos de cargar.
    send("document_ready");
});

/**
 * Muestra la pantalla de confirmacion de la apertura
 * @param {Array} data - un array con los datos a mostrar en la pantalla
 */
function pantalla_confirmacion_apertura(data) {
    // traemos el template
    fetch_template("confirmacion", "pantallas/apertura").then(
        (template_confirmacion) => {
            // decodificamos la imagen.
            const img = decodeURIComponent(data[1]);

            const template_data = {
                titulo: data[0],
            };
            // armamos la pantalla.
            const html_pantallas = template_confirmacion(template_data);
            const contenedor_confirmacion = document.querySelector(
                "#contenedor-confirmacion-apertura"
            );
            contenedor_confirmacion.innerHTML = html_pantallas;
            const texto_confirmacion = document.querySelector(
                ".texto-confirmacion"
            );
            texto_confirmacion.innerHTML = img;
            // hookeamos los eventos
            document
                .querySelector(".aceptar")
                .addEventListener("click", confirmar_apertura);
            document
                .querySelector(".cancelar")
                .addEventListener("click", cancelar_apertura);
            // aplicamos la internacionalizacion
            place_text(constants.i18n);
            // mostramos la pantalla
            document.querySelector(
                "#contenedor-confirmacion-apertura"
            ).style.display = "block";
        }
    );
}

/**
 * Muestra el mensaje de "proxima acta"
 */
function pantalla_proxima_acta(data) {
    document.querySelector("#acciones").style.display = "none";
    document.querySelector("#imprimiendo").style.display = "none";
    document.querySelector("#otra_acta").style.display = "";
}

/**
 * Muestra el mensaje de "imprimiendo"
 */
function imprimiendo() {
    document.querySelector("#acciones").style.display = "none";
    document.querySelector("#otra_acta").style.display = "none";
    document.querySelector("#imprimiendo").style.display = "";
}

/**
 * callback del click de confirmacion de apertura
 */
function confirmar_apertura() {
    imprimiendo();
    send("msg_confirmar_apertura", true);
}

/**
 * callback del click de cancelacion de apertura
 */
function cancelar_apertura() {
    send("msg_confirmar_apertura", false);
}

/**
 * muestra el elemento body del html.
 */
function show_body() {
    document.body.style.display = "block";
}

/**
 *  Genera el popup de papel no puesto
 */
function msg_papel_no_puesto() {
    const generador_html = (template_popup) => {
        const mensaje = constants.i18n.papel_no_puesto;
        const template_data = {
            pregunta: mensaje,
            btn_aceptar: true,
            btn_cancelar: false,
        };
        return template_popup(template_data);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}

/**
 * Genera el popup de "apertura no almacenada" (error de registro)
 */
function msg_apertura_no_almacenada() {
    const generador_html = (template_popup) => {
        const mensaje = constants.i18n.apertura_no_almacenada;
        const template_data = {
            pregunta: mensaje,
            btn_aceptar: true,
            btn_cancelar: false,
        };
        return template_popup(template_data);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}
