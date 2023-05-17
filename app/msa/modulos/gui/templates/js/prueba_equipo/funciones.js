function document_ready() {
    preparar_eventos();
    $(document).bind("dragstart", function (event) {
        event.target.click();
    });
    load_ready_msg();
    $(".popup-box").on("hideDialogo", restaurar_foco_invalido);
}

$(document).ready(document_ready);



function salir() {
    send("salir");
}

function _i18n(key){
    var texto = constants.i18n[key];
    return texto;
}

function show_body() {
    /**/
}
