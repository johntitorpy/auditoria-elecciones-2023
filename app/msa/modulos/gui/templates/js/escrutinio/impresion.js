/**
 * @namespace js.escrutinio.impresion
 */

/**
 * Funciones relacionadas con las pantallas de impresión de actas.
 */

/**
 * Envia al backend la señal de iniciar secuencia de impresion.
 */
function iniciar_secuencia_impresion() {
    send("iniciar_secuencia_impresion");
}

/**
 * Pantalla que pide el acta de escrutinio.
 *
 * @param {*} datos - Contiene la imagen y el tipo de acta.
 */
function pantalla_pedir_acta(datos) {
    var img_element = "<img src= 'img/"+datos.tipo+".png'/>";
    var imagen = document.querySelector("#pantalla_pedir_acta .imagen");

    imagen.firstChild && imagen.firstChild.remove();
    imagen.innerHTML = img_element;
    var texto_insercion_acta = constants.i18n["introduzca_acta_" + datos.tipo];
    document.querySelector(
        "#pantalla_pedir_acta #texto_insercion_acta"
    ).innerHTML = texto_insercion_acta;

    patio.pantalla_pedir_acta.only();
}

/** Muestra la pantalla de copias de actas. */
function pantalla_copias(copia_de, datos_qr) {
    // var texto_insercion_acta = constants.i18n.introduzca_acta_escrutinio;
    const texto_insercion_acta =
        copia_de === "recuento"
            ? constants.i18n.mensaje_copias_recuento
            : copia_de === "escrutinio"
            ? constants.i18n.mensaje_copias_escrutinio
            : copia_de === "certificado"
            ? constants.i18n.acerque_acta_cierre
            : "";
    document.querySelector(
        "#pantalla_pedir_acta #texto_insercion_acta"
    ).innerHTML = texto_insercion_acta;

    document.querySelector("#_txt_mensaje_copias").innerHTML = texto_insercion_acta;

    const qr_element = document.querySelector("#qr_copias_certificado");
    const qr_src_cargado = 
        typeof qr_element.src !== 'undefined' && 
        qr_element.src !== false && 
        qr_element.src !== "";

    if(qr_src_cargado){
        document.querySelector("#qr_copias_certificado").style.display = "";
    }else if(datos_qr != null){
        var svg_data = decodeURIComponent(datos_qr);
        document.querySelector("#qr_copias_certificado").setAttribute("src", svg_data);
    }else{
        document.querySelector("#qr_copias_certificado").style.display = "none";
    }

    patio.pantalla_copias.only();
}

/** Muestra el popup del recuento. */
function mensaje_popup_recuento() {
    const generador_html = (template_popup) => {
        var mensajes = {
            alerta: constants.i18n.recuento_no_almacenado_alerta,
            aclaracion: constants.i18n.recuento_no_almacenado_aclaracion,
        };
        return generar_popup(template_popup, mensajes);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}

/** Muestra el mensaje de acta de transmisión no almacenada.*/
function mensaje_popup_transmision() {
    const generador_html = (template_popup) => {
        var mensajes = {
            alerta: constants.i18n.transmision_no_almacenada_alerta,
            aclaracion: constants.i18n.transmision_no_almacenada_aclaracion,
        };
        return generar_popup(template_popup, mensajes);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}

/**
 * Muestra el mensaje de acta de escrutinio no almacenada.
 *
 * @param {Function} callback - Acción a ejecutarse luego de ocultar el mensaje "imprimiendo".
 */
function mensaje_popup_escrutinio(callback) {
    const generador_html = (template_popup) => {
        var mensajes = {
            alerta: constants.i18n.certificado_no_impreso_alerta,
            aclaracion: constants.i18n.certificado_no_impreso_aclaracion,
        };
        return generar_popup(template_popup, mensajes, callback);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}
/** Muestra el mensaje de certificado de escrutinio no almacenada.*/
function mensaje_popup_certificado() {
    return mensaje_popup_escrutinio(show_slide);
}

/** Muestra el mensaje de copia fiel de escrutinio no almacenada.*/
function mensaje_popup_copia_fiel() {
    return mensaje_popup_escrutinio();
}

/**
 * Genera el popup a mostrar.
 *
 * @param {*} mensajes - Mensajes a mostrar en popup.
 * @param {Function} callback - Acción a ejecutarse luego de ocultar el mensaje "imprimiendo".
 */
function generar_popup(template, mensajes, callback) {
    ocultar_mensaje_imprimiendo(callback);
    var template_data = {
        alerta: mensajes.alerta,
        aclaracion: mensajes.aclaracion,
        btn_aceptar: true,
        btn_cancelar: false,
    };
    var html_contenido = template(template_data);
    return html_contenido;
}

/** Muestra el mensaje de "imprimiendo". */
function mensaje_imprimiendo() {
    patio.mensaje_imprimiendo.only();
}

/**
 * Oculta mensaje de "imprimiendo".
 *
 * @param {Function} callback - Acción a ejecutarse luego de ocultar el mensaje "imprimiendo".
 */
function ocultar_mensaje_imprimiendo(callback) {
    const mensaje_en_pantalla = is_visible(
        document.getElementById("mensaje_imprimiendo")
    );
    if (!mensaje_en_pantalla) return;

    const hay_callback = typeof callback === "function";
    if (hay_callback) return callback();

    patio.pantalla_pedir_acta.only();
}

const svg_from_xml = (xml, mime_type = "image/svg+xml") => {
    return new DOMParser().parseFromString(xml, mime_type).documentElement;
};
