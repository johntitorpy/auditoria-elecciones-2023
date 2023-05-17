/**
 * @namespace js.calibrador.calibrador
 */
'use strict';

// Estados y configuraciones del SVG
var punto_actual = null;
var clicks_usuario = {};
var click_usuario = null;
var tiempo_click_correcto = false;
var punto_verificador = null;
var puntos_pendientes = null;

var get_url = null;

var textos = null;
var th_adyacente = null;
var th_duplicado = null;
var th_errores = null;
var errores = 0;
var esperando_verificacion = false;

var interval = null;
var max_timeout = 500;
var progress_speed = 10
var	timeout = null;
var timeout_value = 0;

function _timeout(){
	if (timeout_value <= max_timeout){
		timeout_value += progress_speed;
        console.log('sumando timeout', timeout_value);
	}else{
        console.log('Tiempo de click alcanzado')
        tiempo_click_correcto = true;
        verificar_click(click_usuario);
	}
}

function limpiar_timeout(){
    if (max_timeout != 0){
        window.clearInterval(timeout);
        timeout = null;
        timeout_value = 0;
    }
}

const ready_calibrador = callback => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

/** Se lanza cuando se termina de cargar la pagina. Establece el contexto.*/
ready_calibrador(() => {
    get_url = get_url_function(`calibrador`);

    document.ontouchstart = (e) => {
        let el = document.querySelector(`.mensaje-estado`);
        el.innerHTML = textos.msj_calibrando;
        el.classList.remove(`error`);
        el.classList.remove(`correcto`);

        tiempo_click_correcto = false;

        if (max_timeout != 0){
            limpiar_timeout();
            timeout = setInterval(_timeout, progress_speed);
        }

        click_usuario = [e.touches[0].screenX, e.touches[0].clientY];
        console.log('Punto de click: ', click_usuario);
    }

    document.onmousemove = (e) => {
        // Solamente se guardan los datos del movimiento del click si
        // se lo espera y no se cambió de puntero.
        if (click_usuario !== null && ! tiempo_click_correcto) {
            // Almaceno el promedio de los clicks anteriores con el actual
            click_usuario = [Math.round((click_usuario[0] + e.x) / 2),
                             Math.round((click_usuario[1] + e.y) / 2)];
        }
    }

    document.ontouchend = (e) => {
        // Evitando que si hay múltiples eventos de touchend no reverifique
        // un click.
        if (click_usuario !== null){
            if (timeout_value > max_timeout){
                tiempo_click_correcto = true;  
            }
            verificar_click(click_usuario);
        } 
    }

    document.oncontextmenu = (e) => {
        // Evitando que se abra el menú
        e.preventDefault();
    }

    send(`inicializar`);
})

/**
 * Muestra el mensaje "msj_inicio_calibracion".
 */
function configurar_textos () {
    let el = document.querySelector(`.titulo`);
    el.innerHTML = textos.titulo;

    el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.msj_inicio_calibracion;
}

/**
 * Se ejecuta cuando estamos listos para empezar a calibrar.
 * 
 * @param {*} data - Datos tales como el locale, el punto de verificación, etc. 
 */
function calibrador_ready(data) {
    if(!data.mostrar_cursor){
        document.querySelector('html').style.cursor = 'none';
    }
    textos = data.locale;
    configurar_textos();

    punto_verificador = data.punto_verificacion;
    puntos_pendientes = data.orden;
    th_adyacente = data.th_adyacente;
    th_duplicado = data.th_duplicado;
    th_errores = data.th_errores;
    // Inicializando el primer punto
    cambiar_punto();

    for (let clave in data.posiciones) {
        let posicion = data.posiciones[clave];
        posicionar_punto(clave, posicion[0], posicion[1]);
    }
    posicionar_punto(`c`, punto_verificador[0], punto_verificador[1])
}

/**
 * Configura la posición del punto verificador.
*/
function posicionar_punto (punto, x, y) {
    const el_punto = document.querySelector(`.punto-${punto}`);
    el_punto.style.left = `${x}px`;
    el_punto.style.top = `${y}px`;
}
/**
 * Reinicia el calibrador.
 * 
 * @param {*} data - Datos tales como el orden, el punto de verificación, etc. 
 */
function reiniciar(data){
    console.log(data);
    errores = 0;
    punto_actual = null;
    esperando_verificacion = false;
    clicks_usuario = {};
    click_usuario = null;
    tiempo_click_correcto = false;
    punto_verificador = data.punto_verificacion;
    puntos_pendientes = data.orden;

    let el_puntos = document.querySelectorAll(`.punto-calibracion`);

    for (let el of el_puntos) {
        el.classList.remove(`detectado`);
        el.classList.add(`pendiente`);
    }

    cambiar_punto();
    posicionar_punto(`c`, punto_verificador[0], punto_verificador[1]);
}

/**
 * Solicita al usuario hacer clic en un nuevo punto o, 
 * en caso de ser el último clic, envía al backend el mensaje "calibrar".
 */
function cambiar_punto() {
    let el_punto = document.querySelector(`.punto-${punto_actual}`);
    if (el_punto !== null) el_punto.classList.add(`detectado`);

    if (puntos_pendientes.length > 0) {
        punto_actual = puntos_pendientes.pop();
        el_punto = document.querySelector(`.punto-${punto_actual}`);
        el_punto.classList.remove(`pendiente`);
    } else {
        console.log("Calibrando...", clicks_usuario);
        send(`calibrar`, clicks_usuario);
    }
}

/**
 * Muestra el mensaje "msj_fin_calibracion".
 */
function verificar_calibracion () {
    const el_punto = document.querySelector(`.punto-c`);
    el_punto.classList.remove(`pendiente`);

    let el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.msj_fin_calibracion;

    esperando_verificacion = true;
}


/**
 * Cuenta la cantidad de clics adyacentes. 
 * 
 * @param {*} click_actual - El último clic realizado.
 */
function obtener_adyacentes(click_actual) {
    let adyacentes = [];
    for (let punto in clicks_usuario) {
        let click_previo = clicks_usuario[punto];
        if (Math.abs(click_actual[0] - click_previo[0]) <= th_adyacente ||
            Math.abs(click_actual[1] - click_previo[1]) <= th_adyacente) {
            adyacentes.push(click_previo);
        }
    }
    return adyacentes;
}

/**
 * Cuenta la cantidad de clics duplicados. 
 * 
 * @param {*} click_actual - El último clic realizado.
 */
function obtener_duplicados(click_actual) {
    let duplicados = [];
    for (let punto in clicks_usuario) {
        let click_previo = clicks_usuario[punto];
        if (Math.abs(click_actual[0] - click_previo[0]) <= th_duplicado &&
            Math.abs(click_actual[1] - click_previo[1]) <= th_duplicado) {
            duplicados.push(click_previo);
        }
    }
    return duplicados;
}

/**
 * Se verifica que el clic es correcto y de ser así 
 * se llama a la función :func:`click_correcto <js.calibrador.calibrador.click_correcto>`,
 * caso contrario, 
 * se muestra un mensaje de error y se envía al back el mensaje "reiniciar".
 * @param {*} click_actual - El último clic realizado.
 */
function verificar_click (click_actual) {
    limpiar_timeout();
    if (! tiempo_click_correcto) {
        errores++;
        if (errores < th_errores) error_click_tiempo();
        else {
            let el = document.querySelector(`.mensaje-estado`);
            el.innerHTML = textos.msj_reinicio_calibracion_error;
            el.classList.add(`error`);
            console.log("Reiniciando la calibración...por TIEMPO");
            send(`reiniciar`);
        }
    } else {
        // Si no se espera la verificación entonces se trata a los clicks como
        // si fuesen los 4 primeros
        if (! esperando_verificacion) {
            let clicks_adyacentes = obtener_adyacentes(click_actual);
            let clicks_duplicados = obtener_duplicados(click_actual);

            if (tiempo_click_correcto) {
                // Si hay almenos un click ya realizado por el usuario, el
                // actual debe ser adyacente, sinó se trata de un error.
                if (Object.keys(clicks_usuario).length > 0) {
                    if (clicks_adyacentes.length == 0) {
                        errores++;
                        if (errores < th_errores) error_click_incorrecto();
                        else {
                            let el = document.querySelector(`.mensaje-estado`);
                            el.innerHTML = textos.msj_reinicio_calibracion_error;
                            el.classList.add(`error`);
                            console.log("Reiniciando la calibración...por CLICK INCORRECTO");
                            send(`reiniciar`);
                        }
                    } else if (clicks_duplicados.length > 0) {
                        errores++;
                        if (errores < th_errores) error_click_duplicado();
                        else {
                            console.log("Reiniciando la calibración...por DUPLICADO");
                            let el = document.querySelector(`.mensaje-estado`);
                            el.innerHTML = textos.msj_reinicio_calibracion_error;
                            el.classList.add(`error`);
                            send(`reiniciar`);
                        }
                        errores++;
                    } else {
                        errores = 0;
                        click_correcto();
                    }
                } else {
                    click_correcto();
                }
            } else {
                errores++;
                if (errores < th_errores) error_click_tiempo();
                else {
                    console.log("Reiniciando la calibración...por TIEMPO");
                    let el = document.querySelector(`.mensaje-estado`);
                    el.innerHTML = textos.msj_reinicio_calibracion_error;
                    el.classList.add(`error`);
                    send(`reiniciar`);
                }
            }
        } else {
            if (Math.abs(click_actual[0] - punto_verificador[0]) <= th_duplicado &&
                Math.abs(click_actual[1] - punto_verificador[1]) <= th_duplicado) {
                // El punto de verificación coincide con el click realizado por el
                // por el usuario así que se termina el proceso de calibración
                send(`terminar`);
            } else {
                console.log("Reiniciando la calibración...");
                // Como no coincide el click con el esperado, se reinicia el proceso
                // de calibración
                let el = document.querySelector(`.mensaje-estado`);
                el.innerHTML = textos.msj_reinicio_calibracion_verif;
                el.classList.add(`error`);
                send(`reiniciar`);
            }
        }
    }
}

/**
 * Muestra el mensaje "textos.msj_sig_punto".
 */
function click_correcto() {
    console.log("click OK");
    clicks_usuario[punto_actual] = click_usuario;
    click_usuario = null;
    errores = 0;
    cambiar_punto();

    let el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.msj_sig_punto;
}

/**
 * Muestra el mensaje "textos.error_misclick".
 */
function error_click_incorrecto () {
    console.log("Error click INCORRECTO, errores alcanzados: ", errores);
    let el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.error_misclick;
    el.classList.add(`error`);
}

/**
 * Muestra el mensaje "textos.error_doubleclick".
 */
function error_click_duplicado () {
    console.log("Error click DUPLICADO, errores alcanzados: ", errores);
    let el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.error_doubleclick;
    el.classList.add(`error`);
}

/**
 * Muestra el mensaje "textos.error_time".
 */
function error_click_tiempo () {
    console.log("Error click TIEMPO, errores alcanzados: ", errores);
    let el = document.querySelector(`.mensaje-estado`);
    el.innerHTML = textos.error_time;
    el.classList.add(`error`);
}


