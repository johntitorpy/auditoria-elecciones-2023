/**
 * @namespace js.escrutinio.recuento
 */

// escrutinio/ipc.js
/* global constants */
/* global sonido_tecla */

// escrutinio/local_controller.js
/* global local_data */

// escrutinio/base.js
/* global patio */

// escrutinio/tabla.js
/* global borrar_resaltado */
/* global actualizar_tabla */

// escrutinio/mensajes.js
/* global mensaje_pocas_boletas */
/* global mensaje_fin_escrutinio */

// escrutinio/clasificacion.js
/* global cargar_clasificacion_de_votos */

// helpers.js
/* global fetch_template */

// handlebars.js
/* global Handlebars */

/**
 * Muestra la pantalla inicial.
 */
function pantalla_inicial() {
    var pantalla = patio.pantalla_inicial;
    pantalla.only();
}

/**
 * Muestra la pantalla de boleta nueva.
 */
function pantalla_boleta_nueva() {
    var pantalla = patio.pantalla_boleta;
    pantalla.only();
}

/**
 * Muestra la pantalla de boleta repetida.
 */
function pantalla_boleta_repetida(data) {
    var contenedor = document.querySelector(
        "#pantalla_boleta_repetida #boleta"
    );
    mostrar_imagen_boleta(data, contenedor);
    var pantalla = patio.pantalla_boleta_repetida;
    pantalla.only();
}

/**
 * Muestra la pantalla de error de lectura de boleta.
 */
function pantalla_boleta_error() {
    var pantalla = patio.pantalla_boleta_error;
    pantalla.only();
}

/**
 * Ejecuta una función para pasar a la pantalla siguiente.
 */
function click_secuencia() {
    var func = patio[patio.last_shown].pantalla_siguiente;
    if (typeof func !== "undefined") {
        func();
    }
}

/**
 * Muestra la pantalla de verificación de acta (para comprobar tag/impreso).
 */
function pantalla_verificar_acta(data) {
    var last_tile = patio.last_shown;
    var contenedor = document.querySelector("#pantalla_verificar_acta #boleta");
    mostrar_imagen_boleta(data, contenedor);
    var pantalla = patio.pantalla_verificar_acta;
    pantalla.only();
    // volver a los 5 segundos a la pantalla anterior:
    function _volver() {
        patio[last_tile].only();
    }
    setTimeout(_volver, 5000);
}

/**
 * Finaliza recuento de boletas.
 */
function finalizar_recuento_boletas() {
    sonido_tecla();
    borrar_resaltado();
    var boletas_procesadas = Number(
        document.querySelector(".numero-procesada").innerHTML
    );

    if (
        boletas_procesadas < constants.MINIMO_BOLETAS_RECUENTO &&
        !constants.totalizador
    ) {
        mensaje_pocas_boletas();
    } else if (constants.totalizador) {
        mensaje_fin_escrutinio();
    } else {
        cargar_clasificacion_de_votos();
    }
}

/**
 * Devuelve los datos a usar en la populación del template del panel de estado.
 */
function popular_panel_estado() {
    return { numero_mesa: constants.numero_mesa };
}

/**
 * Renderiza en pantalla una boleta nueva de recuento apoyada.
 * Realiza todas las acciones relativas a ese evento.
 */
function boleta_nueva(data) {
    templateClass.generar_paneles_confirmacion(data).then((html) => {
   
        var contenedor = document.querySelector("#pantalla_boleta #resultado");
        if (data.seleccion !== null) {
            contenedor.style.display = "block";
            contenedor.innerHTML = html;
        } else {
            contenedor.style.display = "none";
        }
        let total_candidatos = data.seleccion.length;
        asignar_grilla_de(contenedor, total_candidatos);
    });

    var contenedor = document.querySelector("#pantalla_boleta #boleta");
    mostrar_imagen_boleta(data, contenedor);
    pantalla_boleta_nueva();
    actualizar_tabla(data);
    actualizar_boletas_procesadas(data.boletas_procesadas);
}

/*
 * Llamada intermedia para ver si agregamos "efecto" de vacío entre dos
 * boletas contadas o nos ahorramos ese tiempo porque la boleta contada
 * anterior fue error o repetida
 */
function actualizar_boleta(data) {
    function _inner() {
        boleta_nueva(data);
        /*
        * Caso especial donde se apreta por error el botón finalizar luego
        * de contabilizar una boleta nueva.
        */
        if(_en_clasificacion){
            document.querySelector("#cantidad_escrutadas").style.display = "";
            send("habilitar_recuento");
            _en_clasificacion = false;
        }
    }
    setTimeout(_inner, 200);
}

/**
 * Muestra en pantalla la imagen de la boleta del tamaño correcto, en el lugar indicado.
 *
 * @param {*} data - Imagen de la boleta.
 * @param {*} contenedor - Elemento html donde se coloca la imagen de la boleta.
 */
async function mostrar_imagen_boleta(data, contenedor) {
    const muestra_html = constants.muestra_svg
    let iframe_boleta, img_data
    if(data.datos_boleta){
        img_data = JSON.stringify(data.datos_boleta)
    } else {
        img_data = data.imagen
    }
    iframe_boleta = await inserta_imagen_boleta(muestra_html, contenedor, img_data)
    if (iframe_boleta) {
        iframe_boleta.width = '2300px'
        iframe_boleta.height = '832px'
    }
}

function asignar_grilla_de(contenedor, total_candidatos) {
    const classname_grilla = classname_segun_candidatos(
        total_candidatos,
        "max-",
        [1, 2, 3, 4, 5, 6, 8, 10]
    );
    Array.from(
        contenedor.getElementsByClassName("contenedor-votado")
    ).forEach((elemento) => elemento.classList.add(classname_grilla));
}

/**
 * Actualiza la pantalla colocando el nuevo número de boletas procesadas.
 *
 * @param {*} cantidad - Número de boletas procesadas.
 */
function actualizar_boletas_procesadas(cantidad) {
    document.querySelector(".numero-procesada").innerHTML = cantidad;
}

/**
 * Función que devuelve un nombre de clase css de acuerdo a la cantidad de candidatos.
 * El nombre de la clase se arma con el prefijo más el sufijo correspondiente.
 * El sufijo correspondiente es el primer sufijo de ``sufijos_existentes`` que es igual o
 * mayor al valor de ``cantidad_candidatos``. Si no hay ningún sufijo que cumpla con
 * esa condición se devuelve el ultimo sufijo de la lista de ``sufijos_candidatos``.
 * Ejemplos: Si la lista de sufijos es [2, 3, 4, 6, 9, 12, 16, 20, 24, 30, 36] y el
 * prefijo es "max", si la cantidad de candidatos es 24 la salida de la función es
 * "max24"; si es 25, "max30"; si es 31, "max36" y si es 42, "max36".
 * @param {number} cantidad_candidatos - Cantidad de candidatos a mostrar en pantalla.
 * @param {string} prefijo - prefijo de la clase css.
 * @param {number[]} sufijos_existentes - Sufijos existentes de clases css.
 */
const classname_segun_candidatos = (
    cantidad_candidatos,
    prefijo = "max",
    sufijos_existentes = constants.numeros_templates
) =>
    prefijo +
    (sufijos_existentes
        .slice() // genera una copia (para no mutar el arreglo original)
        .sort((a, b) => a - b) // ordena el arreglo de menor a mayor
        .find((i) => i >= cantidad_candidatos) ||
        sufijos_existentes.slice(-1)[0]);
// toma el primer elemento que satisface la condicion, de
// no encontrar uno, devuelve el último elemento del arreglo.

/* exported pantalla_inicial */
/* exported pantalla_boleta_nueva */
/* exported pantalla_boleta_repetida */
/* exported pantalla_boleta_error */
/* exported click_secuencia */
/* exported pantalla_verificar_acta */
/* exported finalizar_recuento_boletas */
/* exported popular_panel_estado */
/* exported actualizar_boleta */
