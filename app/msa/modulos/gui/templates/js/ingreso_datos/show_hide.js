/**
 * @namespace js.ingreso_datos.show_hide
 */

 'use strict';
 /**
  * Recibe selector del dom y llama a la función que los muestra en pantalla. 
  * Para finalizar ejecuta la función ``callback``
  * 
  * @param {string} selector 
  * @param {function} callback 
  */
function show_elements(selector, callback) {
    set_selector_display(selector, "block")
    if ( callback === "function" ) callback();
}

/**
 * Recibe selector del dom y llama a la función que los oculta. 
 * Para finalizar ejecuta la función ``callback``.
 * 
 * @param {string} selector. 
 * @param {function} callback.
 */
function hide_elements(selector, callback) {
    set_selector_display(selector, "none")
    if ( callback === "function" ) callback();
}

/**
 * @function
 * @description Setea la propiedad "display" de los elementos del dom que se toman
 * a partir del selector dado.
 * @param {string} selector - Selector con el cual se tomaran los elementos del DOM.
 * @param {string} display_prop - Valor a setear. Puede ser "none" (oculta el elemento) o "block" (lo muestra) 
 */
const set_selector_display = (selector, display_prop) => {
    const elems = Array.from( document.querySelectorAll(selector) );
    elems.forEach( (e) => e.style.display = display_prop )
}

/**
 * Muestra dialogo de confirmación.
 * 
 */
function show_dialogo_confirmacion() {
    mostrar_mensaje(constants.i18n.confirma_datos_correctos,
                    click_boton_confirmacion);
}

/**
 * Oculta todos los elementos de la pantalla y ejecuta una función callback.
 * @param {Function} callback 
 */
function hide_all(callback) {
    //En apertura
    hide_elements("#pantalla_inicio");
    hide_elements("#contenedor_opciones"); 
    hide_elements("#pantalla_confirmaciondatos");
    // En recuento
    hide_elements(".contenedor-datos");
    hide_elements(".contenedor-opciones-recuento");
    hide_elements(".contenedor-izq");
    hide_elements(".contenedor-der", callback);
}

