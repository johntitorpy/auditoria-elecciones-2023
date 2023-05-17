/**
 * @namespace js.capacitacion.funciones
 */
'use strict';

var _ubicaciones = null;

/**
 * Devuelve el valor de la clave "key".
 *  
 * @param {*} key - Clave del diccionario "constants.i18n".
 */
function _i18n(key){
    var texto = constants.i18n[key];
    return texto;
}

/** Registra el helper de internacionalizacion. */
function registrar_helper_i18n(){
    Handlebars.registerHelper("i18n", _i18n);
}

/** 
 * Configura la mesa para usar el simulador de sufragio de la ubicacion cliqueada.
*/
function click_boton_simulador(event){
    send("configurar_mesa", ["sufragio", event.currentTarget.id.split("_")[1]]);
}

/** 
 * Configura la mesa para usar el simulador de asistida de la ubicacion cliqueeada.
*/
function click_boton_asistida(event){
    send("configurar_mesa", ["asistida", event.currentTarget.id.split("_")[1]]);
}

/**
 * Callback llamada cuando se hace click en el boton de impresión de la boleta en blanco.
 */
function click_boton_boleta(event){
    activar_impresion(event.currentTarget.id.split("_")[1]);
}

function mensaje_impresion_boleta(){
    var dic_ = {
        pregunta: constants.i18n.inserte_boleta_capacitacion,
        aclaracion: constants.i18n.imprimira_voto_en_blanco,
        alerta: constants.i18n.imprimir_boleta_demostracion,
        btn_cancelar: true,
    };
    cargar_dialogo_default(dic_).then(() => {
        document.querySelector(".btn-cancelar").addEventListener("click", () => { cancelar_impresion() });
    })
    encender_led_espera_boleta();
}

function mensaje_boleta_registrando(){
    var dic_ = {
        //TODO alerta: constants.i18n.boleta_imprimiendo,
        alerta: "La boleta aún se esta registrando. Espere a que finalice el proceso de impresión",
        btn_aceptar: true,
    };
    cargar_dialogo_default(dic_).then(() => {
        document.querySelector(".btn-aceptar").addEventListener("click", () => { hide_dialogo() });
    })
}

/** Abre una ubicacion y muestra los juegos de datos dentro de la misma.*/
function click_boton(event){
    var indice = event.currentTarget.dataset.indice;
    fetch_template("boton_ubicacion", "pantallas/capacitacion").then((template_boton_ubicacion) => {
        cargar_botones_ubicacion(_ubicaciones[indice], template_boton_ubicacion);
    });
}

/** 
 * Configura la mesa para usar el simulador de sufragio de la ubicacion cliqueada.
*/
function click_boton_volver(){
    cargar_botones_ubicaciones(_ubicaciones);
}

/**
 * Muestra el mensaje de error de impresion.
 */
function error_impresion_boleta(){
    var dic_ = {
        alerta: constants.i18n.error_imprimir_boleta_demostracion,
        btn_aceptar: true,
    };
    cargar_dialogo_default(dic_).then(() => {
        document.querySelector(".btn-aceptar").addEventListener("click", () => { hide_dialogo()});
    })
}

/**
 * Se dispara cuando se terminó de cargar la pagina.
 */
function document_ready(){
    preparar_eventos();
    document.addEventListener('dragstart', (event) => {event.target.click();});

    load_ready_msg();
}

ready(document_ready);

/** 
 * Carga los botones con los nombres de las ubicaciones.
 * Es llamado desde el controlador de capacitacion en el método "cargar_botones". 
*/
function cargar_botones_ubicaciones(data){
    _ubicaciones = data;
    fetch_template("boton_ubicacion", "pantallas/capacitacion").then((template_boton_ubicacion) => {
        if(data.length == 1){
            cargar_botones_ubicacion(data[0], template_boton_ubicacion); 
        } else {
            cargar_seleccion_ubicaciones(data, template_boton_ubicacion);
        }    
    })
}

/** Carga los botones de las ubicaciones. */
function cargar_botones_ubicacion(data, template_boton_ubicacion){
    var columnas = [];
    var items = [];
    
    for (var i=0; i<data.hijos.length; i++){
        var ubicacion = data.hijos[i];

        var data_template = {
            'nro_mesa': ubicacion.id_unico_mesa,
            'descripcion': ubicacion.municipio,
            'extranjera': ubicacion.extranjera,
            'mostrar_boton_impresion': constants.preimpresion_boleta,
            'mostrar_boton_capacitacion': constants.mostrar_boton_capacitacion,
            'mostrar_boton_asistida': constants.mostrar_boton_asistida,
        }

        items.push(data_template);
    }

    var numero_cols = Math.floor(items.length / constants.items_columna);
    if (items.length % constants.items_columna){
        //Si es cero, el número de items por columnas es exacto
        numero_cols = numero_cols + 1;
    }
    var html = template_boton_ubicacion(
        {"ubicaciones": items,
         "numero_cols": numero_cols,
         "titulo": data.descripcion,
        });
    var botones_ubicacion = document.querySelector("#botones-ubicacion");
    botones_ubicacion.innerHTML = html;

    
    document.querySelector("#contenedor_opciones").style.display = 'none';
    var subir_nivel = document.querySelector(".btn .subir_nivel");
    if (subir_nivel != null) {
      subir_nivel.addEventListener("click", () => click_boton_volver() );
    }
    asignar_evento(".btn .demo", (event) => click_boton_simulador(event));
    asignar_evento(".btn .asistida", (event) => click_boton_asistida(event));
    asignar_evento(".btn .imprimir", (event) => click_boton_boleta(event));
}

/** Carga los botones del menu intermedio. */
function cargar_seleccion_ubicaciones(data, template_boton_ubicacion){
    var columnas = [];
    var items = [];
    
    for (var i=0; i<data.length; i++){
        var ubicacion = data[i];

        var data_template = {
            'nro_mesa': ubicacion.numero,
            'descripcion': ubicacion.descripcion,
            'extranjera': false,
            'codigo': ubicacion.codigo,
        }

        items.push(data_template);
    }

    var numero_cols = Math.floor(items.length / constants.items_columna);
    if (items.length % constants.items_columna){
        //Si es cero, el número de items por columnas es exacto
        numero_cols = numero_cols + 1;
    }
    var html = template_boton_ubicacion(
        {"ubicaciones": items, 
         "numero_cols": numero_cols});
    var botones_ubicacion = document.querySelector("#botones-ubicacion");
    botones_ubicacion.innerHTML = html;

    document.querySelector("#contenedor_opciones").style.display = 'none';
    document.querySelectorAll(".btn").addEventListener("click", (event) => click_boton(event) );
}
