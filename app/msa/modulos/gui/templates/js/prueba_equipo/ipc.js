var constants = {};

get_url = get_url_function("voto");

function load_ready_msg() {
    send("document_ready");
}

/**
 * Carga constantes de la aplicación.
 * @param {json} data - Constantes de la aplicación.
 */
function set_constants(data){
    constants = data;
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);    
    });
    if(!constants.mostrar_cursor){
        document.querySelector("body").style.cursos = "none";
    }
}

function seleccionar_acta_a_copiar(acta_a_copiar = null) {
    send("seleccionar_acta_a_copiar", acta_a_copiar);
}

function change_screen(pantalla) {
    func = window[pantalla[0]];
    func(pantalla[1]);
}

function send(action, data) {
    if(window.zaguan === undefined){
        $.ajax({
            url: get_url(action, data),
            timeout: 1000 //in milliseconds
        });
    } else {
        window.zaguan(get_url(action, data));
    }
}
