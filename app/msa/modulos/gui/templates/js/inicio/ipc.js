/**
 * @namespace js.inicio.ipc
 */
"use strict";
let constants = {};

const get_url = get_url_function("voto");

/**
 * Envia mensaje ``document_ready`` al backend.
 */
function load_ready_msg(){
    send('document_ready');
}

/**
 * Carga constantes de la aplicación.
 * @param {json} data - Constantes del front que se reciben desde el backend.
 */
function set_constants(data){
    constants = data;
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);
        
        document.querySelector("#datos_ubicacion").style.display = "none";
    });
    if(!constants.mostrar_cursor){
        document.body.style.cursor = "none";
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

function load_prueba_equipo(){
    send('modulo_prueba_equipo');
}

