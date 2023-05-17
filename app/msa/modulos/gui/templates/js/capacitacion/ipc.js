/**
 * @namespace js.capacitacion.ipc
 */

'use strict';

let constants = null;

const get_url = get_url_function("voto");

 /**
 * Establece las constantes de la aplicacion. 
 * @param {json} data - Constantes de la aplicación.
 */
function set_constants(data){
    constants = data;
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);    
    });
    document.querySelector('.barra-titulo').style.display = 'block';
    if(!constants.mostrar_cursor){
        document.querySelector('.barra-titulo').css('cursor', 'none');
    }
}

/**
 * Envia el evento de document ready al backend. 
 */
function load_ready_msg(){
    registrar_helper_i18n();
    send("document_ready");
}

/**
 * Activa la impresión para la mesa dada enviando al backend el mensaje ``activar_impresion``.
 * @param {*} nro_mesa - Número de mesa a la cual se le desea activar la impresión.
 */
function activar_impresion(nro_mesa){
    send("activar_impresion", nro_mesa);
}

/**
 * Cancela la impresión en la mesa dada enviando al backend el mensaje ``cancelar_impresion``.
 * @param {*} nro_mesa - Número de mesa a la cual se le desea cancelar la impresión.
 */
function cancelar_impresion(){
    send("cancelar_impresion");
}

function encender_led_espera_boleta(){
    send("encender_led_espera_boleta");
}
