/**
 * @namespace js.inicio.funciones
 */
"use strict";

var ultimo_estado = null;
var seleccion_actual = null;
var puede_cambiar_vista = false;

/**
 * Activa/desactiva alto contraste.
 */
function click_alto_contraste(){
    document.body.classList.toggle("alto-contraste");
    ajustar_botones_contraste();
}

/**
 * Muestra pantalla de inicio.
 */
function pantalla_inicio(data){
   show_pantalla_inicio();
}

/**
 * Función ejecutada cuando el documento html termina de renderizarse.
 */
ready(() => {
    preparar_eventos();
    document.addEventListener('dragstart', (e) => { e.target.click() });
    load_ready_msg();
    pantalla_prueba_equipo();
});

function pantalla_prueba_equipo(){
    document.querySelectorAll(".icon-prueba_equipo").forEach((btn) => {
        btn.addEventListener("click", () => load_prueba_equipo());
    });
}
