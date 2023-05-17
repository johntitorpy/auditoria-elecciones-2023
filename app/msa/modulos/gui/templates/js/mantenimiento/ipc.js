/**
 * @namespace js.mantenimiento.ipc
 */
'use strict';

var constants = {}

const get_url = get_url_function("voto");

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
    popular_header().then(() => {
        place_text(data.i18n);
        place_text(data.encabezado);    
    });
    document.querySelector(".barra-titulo").style.display = 'block';
    if(!constants.mostrar_cursor){
        document.querySelector('body').style.cursor = 'none';
    }
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

/** Envía al back-end el mensaje "volume" */
function click_volumen(event){
    var parts = event.currentTarget.id.split("btn_volumen_");
    send("volume", parts[1]);
}

/** Envía al back-end el mensaje "brightness" */
function click_brillo(event){
    var parts = event.currentTarget.id.split("btn_brillo_");
    send("brightness", parts[1]);
}

/** Envía al back-end el mensaje "eject_cd" */
function click_expulsarcd(){
    send("eject_cd");
}

/** Envía al back-end el mensaje "fan_speed" junto con la velocidad del ventilador. */
function click_ventilador(event){
    var parts = event.currentTarget.id.split("btn_velocidad_");
    send("fan_speed", parts[1]);
}

/** Envía al back-end el mensaje "check_fan" */
function send_check_fan(){
    send("check_fan");
}

/** Envía al back-end el mensaje "fan_auto_mode" */
function send_fan_auto_mode(modo){
    send("fan_auto_mode",modo);
}

/** Envía al back-end el mensaje "load_maintenance" */
function send_load_maintenance() {
    send("load_maintenance");
}

/** Envía al back-end el mensaje "refresh_batteries_status" */
function send_refresh_batteries() {
    send("refresh_batteries_status");
}

/** Envía al back-end el mensaje "printer_test" */
function send_printer_test() {
    send("printer_test");
}

/** Envía al back-end el mensaje "printer_test_cancel" */
function send_printer_test_cancel() {
    send("printer_test_cancel");
}

/** Envía al back-end el mensaje "pir_mode" */
function send_pir_mode(modo){
    send("pir_mode",modo);
}

function send_presencia_mode(modo){
    send("presencia_mode", modo); 
}

function send_registro_presencia(presencia){
    send("presencia_registro", presencia);
}

/** Envía al back-end el mensaje "md5check" */
function send_md5check(){
    send("md5check");
}

/** Envía al back-end el mensaje "autofeed_mode" */
function send_autofeed_mode(modo){
    send("autofeed_mode",modo);
}

/** Envía al back-end el mensaje "get_autofeed_mode" */
function get_autofeed_mode(){
    send("get_autofeed_mode");
}

/** 
 * Envía al back-end el mensaje "reset_device" junto con el
 * dispositivo que se desea reiniciar.
*/
function send_resetdevice(device){
    send("reset_device", device);
} 

/** Envía al back-end el mensaje "print_quality" */
function send_printquality(data){
    send("print_quality", data);
}

/** Envía al back-end el mensaje "get_print_quality" */
function get_printquality(){
    send("get_print_quality");
}

/** Envía al back-end el mensaje "refresh" */
function refresh() {
    send("refresh");
}

