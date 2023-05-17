"use strict";

var constants = {}

get_url = get_url_function("voto");

/**
 * Envia el evento de document ready al backend. 
 */
function load_ready_msg(){
    
    send('document_ready');
}

 /**
 * Establece las constantes de la aplicacion. 
 * @param {json} data - Constantes de la aplicación.
 */
 function set_constants(data){
    constants = data;
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);    
    })
    if(!constants.mostrar_cursor){
        document.body.style.cursor = 'none';
        document.querySelector('input').style.cursor = 'none';
        document.querySelector('label').style.cursor = 'none';
    }
}

 /**
 * Llama a la funcion de cambio de pantalla para cierta pantalla. 
 * @param {list} pantalla - Pantalla a la cual se quiere cambiar.
 */
function change_screen(pantalla){
    func = window[pantalla[0]];
    func(pantalla[1]);
}
