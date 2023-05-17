/**
 * @namespace js.ingreso_datos.ipc
 */
var constants = {};

get_url = get_url_function("voto");

/**
 * Envia mensaje de que la página cargó.
 */
function load_ready_msg() {
    send("document_ready");
}

/**
 * Carga constantes de la aplicación.
 * @param {json} data - Constantes de la aplicación.
 */
function set_constants(data) {
    constants = data;
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);

        document.querySelector("#datos_ubicacion").style.display = "none";
    });
    if (!constants.mostrar_cursor) {
        document.querySelector("body").style.cursos = "none";
    }
    console.log(constants)
    inicializarHoraEleccion(constants);
}
/**
 * Llama a la funcion de cambio de pantalla para cierta pantalla
 * @param {Array} pantalla
 */
function change_screen(pantalla) {
    func = window[pantalla[0]];
    func(pantalla[1]);
}
