/**
 * @namespace js.escrutinio.pantallas
 */

/**
* Devuelve los datos a usar en la populacion del template de "pantalla_loader".
*/
function popular_loader(){
    return {
        "cargando_interfaz": constants.i18n.cargando_interfaz,
        "espere_por_favor": constants.i18n.espere_por_favor,
    };
}

/**
* Muestra la pantalla del loader.
*/
function pantalla_loader(){
    var pantalla = patio.pantalla_loader;
    pantalla.only();
}
