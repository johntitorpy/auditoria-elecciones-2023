/**
 * @namespace js.mantenimiento.show_hide
 */
'use strict';

 /** Muestra la pantalla de inicio. */
function show_pantalla_inicio(){
    document.querySelector('#pantalla_inicio').style.display = 'block'
}

 /** Oculta la pantalla de inicio. */
function hide_pantalla_inicio(){
    document.querySelector('#pantalla_inicio').style.display = 'none'
}

 /** Muestra la pantalla de mantenimiento. */
function show_pantalla_mantenimiento(){

    document.querySelector('#btn_inicio').style.display = 'none'
    document.querySelector('#pantalla_mantenimiento').style.display = 'block'
    document.querySelector('#btn_volver_admin').style.display = 'block'
}

function hide_pantalla_mantenimiento(){
 /** Oculta la pantalla de mantenimiento. */

    document.querySelector('#pantalla_mantenimiento').style.display = 'none'
    document.querySelector('#btn_volver_admin').style.display = 'none'
    document.querySelector('#btn_mantenimiento').style.display = 'none'
    document.querySelector('#btn_inicio').style.display = 'block'
    show_pantalla_inicio();
}

/** Muestra el botón de mantenimiento. */
function show_btn_mantenimiento(){
    document.querySelector('#btn_mantenimiento').style.display = 'block'
}

/** Oculta el botón de mantenimiento. */
function hide_btn_mantenimiento(){
    document.querySelector('#btn_mantenimiento').style.display = 'none'
}

/** Muestra el botón de demo. */
function show_btn_demo(){
    document.querySelector('#btn_demo').style.display = 'block'
}

/** Oculta el botón de demo. */
function hide_btn_demo(){
    document.querySelector('#btn_demo').style.display = 'none'
}

/** Muestra el modo ventilador. */
function show_modo_ventilador(){
    document.querySelector('#modo_ventilador').style.display = 'block'
}

/** Oculta el modo ventilador. */
function hide_modo_ventilador(){
    document.querySelector('#modo_ventilador').style.display = 'none'
}


/** Muestra la velocidad de los ventiladores. */
function show_velocidad_ventiladores(){
    document.querySelector('#velocidad_ventiladores').style.display = 'block'
}

/** Oculta la velocidad de los ventiladores. */
function hide_velocidad_ventiladores(){
    document.querySelector('#velocidad_ventiladores').style.display = 'none'
}

/** Muestra el chequeo del ventilador. */
function show_chequeo_ventilador(){
    document.querySelector('#chequeo_ventilador').style.display = 'block'
}

/** Oculta el chequeo del ventilador. */
function hide_chequeo_ventilador(){
    document.querySelector('#chequeo_ventilador').style.display = 'none'

}
