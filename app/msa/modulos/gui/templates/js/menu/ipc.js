/**
 * @namespace js.menu.ipc
 */
'use strict';

let constants = {};

const get_url = get_url_function("voto");

/**
 * Es necesario que tanto "set_constants" como "mostrar_pantalla_menu" hallan sido invocados 
 * desde el controlador para poder mostrar la pantalla.
 */
let precondiciones_mostrar_pantalla = {
    datos: null, // datos que requiere la funcion de mostrar pantalla
    mensajes_controlador: [ // mensajes que se invocan desde el controladory que deben ser completados antes de la llamada a mostrar la pantalla
        {
            "nombre": "set_constants",
            "finalizado": false
        }, {
            "nombre": "mostrar_pantalla_menu",
            "finalizado": false
        }
    ]
}

/**
* Envia la señal "document_ready" al backend.
*/
function load_ready_msg(){
    send('document_ready');
}

/** Envía al back-end el mensaje "load_maintenance" */
function load_mantenimiento(){
    send('load_maintenance');
}


/**
 * Establece las constantes que llegan desde el backend.
 * 
 * @param {*} data - un objeto con las constantes.
 */
function set_constants(data){
    constants = data;
    const promise_patio = load_patio();
    const promise_header = popular_header();
    Promise.all([
        promise_patio,
        promise_header
    ]).then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);
        precondicion_cumplida("set_constants");
        document.querySelector("#datos_ubicacion").style.display = "none";
    });
    document.querySelector(".barra-titulo").style.display = 'block';
    if(!constants.mostrar_cursor){
        document.body.style.cursor = "none";
    }
}

/**
 * Se encarga de orquestar la llamada a mostrar_pantalla. 
 * Para invocar a mostrar_pantalla es necesario que el controlador haya enviado 
 * todos los mensajes definidos en la variable ``precondiciones_mostrar_pantalla``.
 * @param {String} precondicion_mensaje - Mensaje que envió el controlador y que ha sido completado.
 * @param {Object} datos - Datos que requiere la función mostrar_pantalla.
 */
const precondicion_cumplida = (precondicion_mensaje, datos=null) => {
    precondiciones_mostrar_pantalla = actualizar_precondiciones(
        precondiciones_mostrar_pantalla, 
        precondicion_mensaje, 
        datos
    );
    const puede_mostrar_pantalla = precondiciones_mostrar_pantalla.mensajes_controlador.every(
        (mensaje) => mensaje.finalizado
    );
    if (puede_mostrar_pantalla){
        mostrar_pantalla(precondiciones_mostrar_pantalla.datos);
    }
}

/**
 * Actualiza precondiciones (sin mutar la data original). 
 * @param {Object[]} precondiciones - Arreglo con todas las precondiciones.
 * @param {String} mensaje_a_actualizar - Nombre del mensaje a actualizar.
 * @param {Object|null} datos - Nuevo valor de la propiedad "datos". No se actualiza si es nulo.
 * @param {boolean|true} finalizado - Nuevo valor de la propiedad "finalizado".
 */
const actualizar_precondiciones = (precondiciones, mensaje_a_actualizar, datos=null, finalizado=true) => {
    const mensaje_index = precondiciones.mensajes_controlador.findIndex(
        (precondicion) => precondicion.nombre == mensaje_a_actualizar
    )
    if (mensaje_index === -1){
        console.warn(`La precondición ${mensaje_a_actualizar} no es una precondición válida para mostrar la pantalla. No se actualizan las precondiciones.`);
        return precondiciones;
    }

    const mensaje_actualizado = { 
        ...precondiciones[mensaje_index], 
        finalizado
    };

    const mensajes_actualizados = [
        ...precondiciones.mensajes_controlador.slice(0, mensaje_index),
        mensaje_actualizado,
        ...precondiciones.mensajes_controlador.slice(mensaje_index + 1),
    ];

    const datos_actualizados = (datos === null)? {} : {datos};

    const precondiciones_actualizadas = Object.assign(
        {}, 
        precondiciones, 
        datos_actualizados, 
        {mensajes_controlador: mensajes_actualizados}
    )

    return precondiciones_actualizadas;
}

function mostrar_pantalla_menu(datos){
    precondicion_cumplida("mostrar_pantalla_menu", datos);
}

/**
 * Muestra la pantalla dada por parámetro.
 * 
 * @param {*} pantalla - La pantalla que se desea mostrar.
 */
function change_screen(pantalla){
    func = window[pantalla[0]];
    func(pantalla[1]);
}

/** Envía al back-end el mensaje "apagar" */
function apagar(){
    send('apagar');
}

/** Envía al back-end el mensaje "calibrar" */
function calibrar(){
    send('calibrar');
}

/** Envía al back-end el mensaje "click_boton" */
function salir_a_modulo(modulo){
    send("click_boton", modulo);
}
