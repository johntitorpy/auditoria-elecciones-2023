/**
 * @namespace js.mantenimiento.funciones 
 */
'use strict';

let refresh_interval = 0;
let refresh_battery_interval = 0;



ready (() => document_ready());

/**
 * Se dispara cuando se terminó de cargar la pagina.
 */
function document_ready(){
    preparar_eventos();
    document.addEventListener("dragstart", (event) => {
        event.target.click();
    });

    load_ready_msg();

    asignar_evento('.boton-central', click_boton);
    asignar_evento("#accesibilidad li", click_boton)
    asignar_evento('#volumen .boton', click_volumen);
    asignar_evento('#brillo .boton', click_brillo);
    asignar_evento('#velocidad_ventiladores .boton', click_ventilador);
    asignar_evento('#chequeo_ventilador button', click_chequeo_ventilador);
    document.querySelector('#modo_ventilador_checkbox').addEventListener("change", cambio_modo_ventilador);
    document.querySelector('#expulsar_cd').addEventListener("click", click_expulsarcd);
    document.querySelector('#printer_test').addEventListener("click", send_printer_test);
    document.querySelector('#modo_presencia_checkbox').addEventListener("change", cambio_modo_presencia);
    document.querySelector('#chequear_cd').addEventListener("click", click_md5);
    document.querySelector('#modo_autofeed').addEventListener("click", click_modo_autofeed);
    document.querySelector('#reset_devices').addEventListener("click", click_reiniciar_dispositivos);
    document.querySelector('#printing_quality').addEventListener("click", click_calidad_impresion);
    
}


/**
 * Genera el html del popup "mantenimiento_boleta".
 * @returns {Promise} Al completarse la promise se devuelve el string html del popup.
 */
function popular_dialogo_boleta(){
    const generador_html = (template) => {
        return template();
    } 
    return promise_popup("mantenimiento_boleta", "partials/popup", generador_html);
}

/**
* Genera el html del popup "mantenimiento_reset".
* @returns {Promise} Al completarse la promise se devuelve el string html del popup.
*/
function popular_dialogo_reset(){
    const generador_html = (template) => {
        return template();
    } 
    return promise_popup("mantenimiento_reset", "partials/popup", generador_html);
}

/**
* Genera el html del popup "mantenimiento_calidad".
* @returns {Promise} Al completarse la promise se devuelve el string html del popup.
*/
function popular_dialogo_calidad(){
    const generador_html = (template) => {
        return template();
    } 
    return promise_popup("mantenimiento_calidad", "partials/popup", generador_html);

}
/**
 * Envía al back0end el mensaje "click_boton".
 */
function click_boton(event) {
    const parts = event.currentTarget.id.split("btn_");
    if (
        !event.currentTarget.classList.contains("boton-desactivado") &&
        !event.currentTarget.classList.contains("gradiente-blanco")
    ) {
        send("click_boton", parts[1]);
    }
}

/**
 * Inicia el módulo de mantenimiento.
*/
function inicio_mantenimiento() {
    document.querySelector("#brillo").style.display = "block";
    if(constants.usar_pir){
        document.querySelector("#presencia").style.display = "block";
    }
    document.querySelector("#reset_devices").style.display = "";
    //document.querySelector("#modo_autofeed").style.display = "";
    document.querySelector("#printing_quality").style.display = "";

    document.querySelector("#loading").style.display = "none";
    document.querySelector("#pantalla_mantenimiento").style.display = "block";

}

/**
 * Inicia intervalos para recargar información tales como el estado de la batería.
 */
function inicio_intervals(){
    refresh_interval = setInterval(refresh, constants.intervalo_refresco);
    refresh_battery_interval = setInterval(send_refresh_batteries, constants.intervalo_refresco_bateria);
    setTimeout(send_refresh_batteries, 5000);

}

/**
 * Muestra el volumen.
 * 
 * @param {*} data - Contiene el volumen a mostrar. 
 */
function mostrar_volumen(data){
    document.querySelector("#nivel_volumen").innerHTML = data.volumen;
}

/**
 * Muestra el brillo.
 * 
 * @param {*} data - Contiene el brillo a mostrar. 
 */
function mostrar_brillo(data){
    document.querySelector("#nivel_brillo").innerHTML = data.brillo;
}

/**
 * Muestra datos referidos a la batería.
 * El servidor ejecuta esta función en la llamada ``get_battery_status``. Ver controlador 
 * del módulo de Mantenimiento.
 * 
 * @param {*} data - Contiene los datos referidos a la batería. 
 */
function mostrar_bateria(data){
    if(!"baterias" in data || data.baterias === null) return;
    
    const datos_baterias  = data.baterias;
    fetch_template("baterias", "pantallas/mantenimiento").then((template_baterias) => {
        var texto = "";
        if (datos_baterias !== 0) {
            datos_baterias.forEach( (element, index) => {
                var numero_bateria = index + 1;
                var battery_level_number = element.battery_level;
                var battery_level = get_battery_level(battery_level_number);
                var corriente = "";
                if (element.charging) corriente = "charging";
                else if (element.discharging) corriente = "discharging";
                var temp = Math.round(Number(element.temp) * 100) / 100;
                var slot = (element.slot_number == 1)? "derecha" : "izquierda";
                var data_template = {
                    'numero_bateria': numero_bateria,
                    'slot': slot,
                    'battery_level_number': battery_level_number,
                    'battery_level': battery_level,
                    'charging': corriente,
                    'tension': element.tension,
                    'temp': temp,
                    'full_charge': element.full_charge,
                    'remaining': element.remaining,
                    'ciclos': element.ciclos,
                    'corriente': element.corriente
                };
                var item_bateria = template_baterias(data_template);
                texto += item_bateria;
            });
        } else {
            texto += "No hay bater&iacute;as conectadas.<br />";
        }
        texto += "<div class=\"clear\"></div>";
        document.querySelector("#nivel_bateria").innerHTML = texto;
    });
}

/**
 * Muestra el nivel de uso de la batería.
 * 
 * @param {Number} number - Nivel de uso de la batería.
 * @returns {String} Nombre de clase css que describe el nivel de batería.
 */
function get_battery_level(number) {
    let classname = "";
    if (number > 80) classname = "full";
    else if (number > 60 & number <= 80) classname = "3_4";
    else if (number > 40 & number <= 60) classname = "half";
    else if (number > 20 & number <= 40) classname = "1_4";
    else if (number <= 20) classname = "empty";
    return classname;
}

/**
 * Muestra la fuente de la batería.
 * 
 * @param {*} data - Contiene datos sobre la fuente.
 */
function mostrar_fuente_energia(data) {
    const fuente = data.power_source;
    let texto = "<strong>Fuente de energía:</strong> ";
    switch (fuente) {
        case 0:
            texto += "AC";
            break;
        case 1:
            texto += "Batería derecha";
            break;
        case 2:
            texto += "Batería izquierda";
            break;
    }
    document.querySelector("#power_source").innerHTML = texto;
}

/**
 * Muestra datos sobre la placa y el build.
 * 
 * @param {*} data - Los datos de la placa y el build.
 */
function mostrar_build(data){
    const build = data.build;
    const machine = data.machine;
    const texto = `Placa ${machine} -  Build ${build[0]}.${build[1]}.${build[2]}`;
    document.querySelector("#build").innerHTML = texto;
}

/**
 * Muestra datos sobre potencia del chip rfid.
 * 
 * @param {*} data - Datos sobre potencia del chip rfid.
 */
function mostrar_potencia_rfid(data){
    document.querySelector("#nivel_potencia").innerHTML = data.potencia;
}

/**
 * Muestra datos del rfid.
 * @param {*} data - Datos del chip rfid
 */
function mostrar_rfid(data){
    document.querySelector("#espacio_chequeo_rfid").innerHTML = data;
}

/**
 * Muestra la velocidad del ventilador.
 * @param {*} data - Datos sobre la velocidad del ventilador.
 */
function mostrar_velocidad_ventilador(data){
    document.querySelector("#nivel_velocidad").innerHTML = data.velocidad;
}

/**
 * Muestra el modo en el que está configurado el ventilador.
 * 
 * @param {*} data - Datos sobre el modo en el que está configurado el ventilador.
 */
function mostrar_modo_ventilador(data){
    const modo = (data.modo_auto)? "Autom&aacute;tico" : "Manual";
    const texto = `El modo actual es <strong>${modo}</strong>`;
    document.querySelector("#modo_ventilador_actual").innerHTML = texto;
    document.querySelector("#modo_ventilador_checkbox").setAttribute("checked", data.modo_auto);
    if (data.modo_auto) {
        hide_velocidad_ventiladores();
    } else {
        show_velocidad_ventiladores();
    }
    show_modo_ventilador();
    show_chequeo_ventilador();
}

/**
 * Muestra la temperatura de la máquina.
 * @param {*} data - Datos sobre la temperatura de la máquina.
 */
function mostrar_temperatura(data){
    const temperatura = `${data.temperatura}°C`;
    document.querySelector("#nivel_temperatura").innerHTML = temperatura;
}

/**
 * Cambia y muestra el modo en el que está configurado el ventilador.
 * 
 * @param {*} data - Datos sobre el modo en el que está configurado el ventilador.
 */
function cambio_modo_ventilador(event){
    const modo = event.currentTarget.checked;
    if (modo) {
        hide_velocidad_ventiladores();
    } else {
        show_velocidad_ventiladores();
    }
    mostrar_modo_ventilador({'modo_auto': modo});
    send_fan_auto_mode(modo);
}

/**
 * Activa el chequeo del ventilador cada determinada cantidad de tiempo.
 */
function click_chequeo_ventilador(){
    desactivar_chequeo_ventilador();
    setTimeout(send_check_fan, 100);
    setTimeout(activar_chequeo_ventilador, constants.tiempo_desactivacion_chequeo);
}

/**
 * Desactiva el chequeo del ventilador.
 */
function desactivar_chequeo_ventilador(){
    document.querySelector("#chequeo_ventilador button").classList.add("boton-deshabilitado");
    document.querySelector("#modo_ventilador a").classList.add("boton-deshabilitado");
    hide_velocidad_ventiladores();
    document
        .querySelector('#chequeo_ventilador button')
        .removeEventListener('click', click_chequeo_ventilador);
}

/**
 * Activa el chequeo del ventilador.
 */
function activar_chequeo_ventilador(){
    document.querySelector("#chequeo_ventilador button").classList.remove("boton-deshabilitado");
    document.querySelector("#modo_ventilador a").classList.remove("boton-deshabilitado");
    if(!document.querySelector("#modo_ventilador_checkbox").checked){
        show_velocidad_ventiladores();
    }
    document
        .querySelector('#chequeo_ventilador button')
        .addEventListener('click', click_chequeo_ventilador);
}



/**
 * Muestra el estado de presencia.
 * 
 * @param {*} data - Datos que contienen el estado de presencia
 */
function mostrar_estado_presencia(data) {
    var estado = data.estado;
    var texto = (estado)? "Prendido / Detecta presencia" : "Apagado / No detecta presencia";
    document.querySelector("#estado_presencia").innerHTML = texto;
}

/**
 * Muestra diálogo de la impresora.
 * 
 * @param {*} data - Contiene el estado de la impresora. 
 */
function mostrar_test_impresora(data) {
    if (data.estado == 'esperando') {
        cargar_dialogo_default({
            alerta: "Inserte papel en la impresora",
            btn_cancelar: true
        })
    } else if (data.estado == 'imprimiendo') {
        cargar_dialogo_default({
            alerta: "Imprimiendo",
        })
    }
}

/**
 * Oculta el diálogo de la impresora.
 */
function ocultar_test_impresora(){
    hide_dialogo();
}

/**
 * Oculta el diálogo de la impresora y envía al back-end el mensaje de cancelar la impresión.
 */
function click_boton_popup_cancelar(){
    hide_dialogo();
    send_printer_test_cancel();
}


/**
 * Cambia el estado del checkbox de presencia.
 * 
 * @param {*} data - Contiene el dato si se debe bloquear o no presencia.
 */
function bloquear_desbloquear_checkbox(data) {
    document.getElementById("modo_presencia_checkbox").disabled = data.bloqueo;
    if (data.bloqueo) {
        document.getElementById("presencia").classList.add("presencia-disabled");
    } else {
        document.getElementById("presencia").classList.remove("presencia-disabled");
    }
}

function mostrar_modo_presencia(data){
    let presencia_activada = data.presencia_activada;
    document.getElementById("modo_presencia_checkbox").checked = presencia_activada;
    mostrar_estado_presencia({'estado':presencia_activada});
}

/**
 * Muestra el modo de presencia y envía al back-end el mensaje de cambio de modo presencia.
 */
function cambio_modo_presencia(event){
    let presencia_activada = event.currentTarget.checked;
    mostrar_modo_presencia({'presencia_activada': presencia_activada});
    send_presencia_mode(presencia_activada);
    send_registro_presencia(presencia_activada);
}

/**
 * Coloca a un botón la acción de procesar el md5.
 */
function click_md5(){
    cargar_dialogo_default({
        alerta: constants.i18n.texto_md5,
        btn_aceptar: true,
        btn_cancelar: true
    }).then(() => {
        document.querySelector(".popup-box .popup .btn-aceptar").addEventListener("clickBtnPopup", procesando_md5);
    })
}

/**
 * Envía al back-end el mensaje de chequeo del md5 
 * e informa al usuario de que se está procesando.
 */
function procesando_md5(){
    cargar_dialogo_default({
        alerta: "Procesando..."
    }).then(() => {        
        send_md5check()
    })
}

/**
 * Muestra el md5.
 */
function mostrar_md5(data){
    var md5 = data.md5;
    cargar_dialogo_default(
        {
            alerta: md5, 
            btn_aceptar: true
        }
    ).then(() => {
        document.querySelector(".popup-box .popup .btn-aceptar").addEventListener("click", click_boton_popup_cancelar);
    });
}

/**
 * Muestra el auto-feed.
 * @param {*} data 
 */
function mostrar_autofeed(data){
    var autofeed = data.autofeed;
    document.querySelector(".boletas div").classList.remove("seleccionada");
    document.querySelector("#boleta_" + autofeed).classList.add("seleccionada");
}

/**
 * Muestra diálogo con las boletas y agrega a un botón la acción 
 * :func:`click_opcion_autofeed <js.mantenimiento.funciones.click_opcion_autofeed>`.
 */
function click_modo_autofeed(){
    //mostrar popup con las boletas
    cargar_dialogo("popular_dialogo_boleta").then(() => {
        document.querySelector(".popup .cerrar-popup").addEventListener("click", click_boton_popup_cancelar);
        asignar_evento("div.boletas div", click_opcion_autofeed);
        get_autofeed_mode();    
    })
}

/**
 * Envía al back-end el mensaje de modo auto-feed.
 */
function click_opcion_autofeed(event){
    Array.from(
        document.querySelector(".boletas div")
    ).forEach(
        (i) => i.classList.remove("seleccionada")
    )
    event.currentTarget.classList.add("seleccionada");
    const id = event.currentTarget.id;
    const modo = id.split("boleta_")[1];
    hide_dialogo();
    send_autofeed_mode(modo);
}

/**
 * Muestra el dialogo de reinicio de dispositivos y le asigna acciones a sus botones. 
 */
function click_reiniciar_dispositivos(){
    cargar_dialogo("popular_dialogo_reset").then(() => {
        document.querySelector(".popup .cerrar-popup").addEventListener("click", click_boton_popup_cancelar);
        asignar_evento("div.opciones-reset div", click_opcion_reset)    
    })
}

/**
 * Envía al back-end el mensaje de reiniciar dispositivo.
 */
function click_opcion_reset(event){
    var id = event.currentTarget.dataset.dispositivo;
    hide_dialogo();
    send_resetdevice(id);
}

/**
 * Muestra la calidad de la impresión.
 */
function mostrar_print_quality(data){
    Array.from(document.querySelector(".opciones-quality div")).forEach((i) =>
        i.classList.remove("seleccionada")
    );
    const opcion = constants.niveles_impresion.indexOf(data.print_quality);
    document.querySelector(`div[data-calidad='${opcion}']`).classList.add("seleccionada");
}

/**
 * Muestra el dialogo de calidad de la impresión y le asigna acciones a sus botones. 
 */
function click_calidad_impresion(){
    cargar_dialogo("popular_dialogo_calidad").then(() => {
        asignar_evento(".popup .cerrar-popup", click_boton_popup_cancelar);
        asignar_evento("div.opciones-quality div", click_opcion_calidadimpresion);
        get_printquality();    
    });
}

/** Oculta el diálogo y envía al back-end el mensaje "print_quality". */
function click_opcion_calidadimpresion(event){
    Array.from(document.querySelector(".opciones-quality div")).forEach((i) =>
        i.classList.remove("seleccionada")
    );
    event.currentTarget.classList.add("seleccionada");
    const nivel = event.currentTarget.dataset.calidad;
    const valor = constants.niveles_impresion[nivel];
    hide_dialogo();
    send_printquality(valor);
}
