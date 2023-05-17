/**
 * @namespace js.inicio.show_hide
 */
"use strict";
/**
 * Muestra pantalla de inicio.
 */
function show_pantalla_inicio() {
    document.querySelector("#pantalla_inicio").style.display = "";
}

/**
 * Oculta pantalla de inicio.
 */
function hide_pantalla_inicio() {
    document.querySelector("#pantalla_inicio").style.display = "none";
}

function show_icono_prueba_equipo(){
    // $(".icon-prueba_equipo").show();
    document.querySelector('.icon-prueba_equipo').style.display = "";
}

function hide_icono_prueba_equipo(){
    // $(".icon-prueba_equipo").hide();
    document.querySelector('.icon-prueba_equipo').style.display = "none";
}
