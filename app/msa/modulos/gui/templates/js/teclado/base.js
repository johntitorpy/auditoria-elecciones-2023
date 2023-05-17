/**
 * @namespace js.teclado.base
 */
// Variables globales invocadas

// teclado/tiles.js
/* global layouts */
/* global callbacks_especiales */

// popup.js
/* global procesar_dialogo */

// teclado/layouts.js
/* global keyboard_layouts */

// patio.js
/* global Patio */

// zaguan.js
/* global send */

// asistida.js
/* global beep */
/* global apretar_asterisco */
/* global apretar_numeral */

"use strict";

/*
 * @TODO Investigar si esta variable es necesaria
 * en este modulo (zaguan la requiere?).
 */
var get_url = null;

let patio_teclado = null;
let destination = null;
let inputs = [];

/**
 * @function
 * @description Funcion que carga los teclados usando Patio y asocia los callbacks
 * de las teclas.
 * Las opciones son:
 * layout -- lista de layouts que debe cargar. Se corresponden con tiles del Patio cargado.
 * first_input -- indice del primer campo que utiliza el teclado, el índice corresponde a un item de ```inputs```.
 * callback_finish -- funcion callback al llegar al ultimo campo
 *     de carga del formulario
 * @param {Object} contenedor_query_selector - Contenedor en donde se situará el teclado en el DOM.
 * @param {Object} inputs - Inputs que usarán el teclado.
 * @param {Object|{}} options - Opciones de configuración del teclado.
 */
/* exported load_teclados */
const load_teclados = (contenedor_query_selector, teclado_inputs, options) => {
    const default_settings = {
        // These are the defaults.
        layout: ["qwerty"],
        first_input: 0,
        callback_finish: null,
    };

    const settings = Object.assign({}, default_settings, options);

    return new Promise((resolve, reject) => {
        if (patio_teclado !== null) {
            resolve();
            return;
        }
        patio_teclado = new Patio(
            contenedor_query_selector,
            layouts,
            [],
            "partials/teclado"
        );
        patio_teclado
            .load()
            .then(() => {
                settings.layout.forEach((teclado) => {
                    document
                        .querySelectorAll(patio_teclado[teclado].button_filter)
                        .forEach((tecla) => {
                            tecla.addEventListener("mousedown", (event) =>
                                resaltar_letra(event)
                            );
                            tecla.addEventListener("mouseup", (event) =>
                                desresaltar_letra(event)
                            );
                        });
                });
                document.body.addEventListener("mouseup", desresaltar_letra);

                if (typeof settings.callback_finish === "function") {
                    set_callback_aceptar(settings.callback_finish);
                }

                inputs = Array.from(teclado_inputs);
                destination = inputs[settings.first_input];
                load_inputs(inputs);
                const input_to_focus = inputs.find((input) => input.autofocus);
                if (input_to_focus) {
                    input_to_focus.dispatchEvent(new Event("focusout"));
                    input_to_focus.dispatchEvent(new Event("focusin"));
                } else {
                    destination.dispatchEvent(new Event("focusout"));
                    destination.dispatchEvent(new Event("focusin"));
                }
                resolve();
            })
            .catch((error) => {
                console.error("Error cargando teclado.");
                reject(error);
            });
    });
};

/**
 * Parsea los layouts en arrays de diccionarios con todas las teclas.
 *
 * @param {*} id - Id del tile en la configuración de Patio, debe coincidir con el nombre del tile en layouts.
 */
/* exported popular_teclado */
function popular_teclado(id) {
    const keyname = id.slice(1);
    const rows = keyboard_layouts[keyname].map((fila) => {
        if (fila.length <= 0) return [];
        const botones = fila[0].split(" ");
        return botones.map((boton) => {
            if (boton.startsWith("{")) {
                const boton_especial = boton.slice(1, -1).split("|");
                return {
                    texto:
                        boton_especial.length == 2
                            ? boton_especial[1]
                            : boton_especial[0],
                    action_key: true,
                    accion: boton_especial[0].toLowerCase(),
                    classname: "ui-keyboard-" + boton_especial[0].toLowerCase(),
                };
            }
            return {
                texto: boton,
                action_key: false,
                accion: "regular",
                classname: "ui-keyboard-regular",
            };
        });
    });
    return { id: keyname, rows: rows };
}

/**
 * Muestra un mensaje en el area del teclado.
 *
 * @param {String} mensaje - Contenido del mensaje que se muestra, acepta html.
 * @param {Function} callback_positivo - Callback que se llama cuando se presiona aceptar
 * @param {Function} callback_negativo - Callback que se llama cuando se presiona cancelar. En caso de no estar, simplemente oculta el mensaje.
 * @param {Boolean} ocultar_botones - Si se desea ocultar o mostrar los botones de "aceptar" y "cancelar".
 */
/* exported mostrar_mensaje */
function mostrar_mensaje(
    mensaje,
    callback_positivo,
    callback_negativo,
    ocultar_botones
) {
    if (typeof ocultar_botones === "undefined") {
        ocultar_botones = false;
    }
    if (!callback_negativo) {
        callback_negativo = ocultar_mensaje;
    }

    patio_teclado.mensaje.only();

    const selector = patio_teclado.mensaje.id;

    const btn_aceptar = document.querySelector(selector + " .btn-aceptar");
    const btn_cancelar = document.querySelector(selector + " .btn-cancelar");

    if (ocultar_botones) {
        btn_aceptar.style.display = "none";
        btn_cancelar.style.display = "none";
    } else {
        btn_aceptar.style.display = "block";
        btn_cancelar.style.display = "block";
        btn_aceptar.addEventListener("click", callback_positivo);
        btn_cancelar.addEventListener("click", callback_negativo);
    }

    document.querySelector(selector + " .texto").innerHTML = mensaje;
    document.querySelector(".placeholder-confirma").style.display = "block";

    destination.classList.remove("seleccionado");
}

/**
 * Oculta el diálogo de mensaje
 */
function ocultar_mensaje() {
    patio_teclado.mensaje.hide();
    document.querySelector(".placeholder-confirma").style.display = "none";
    procesar_dialogo(false);
    destination.classList.add("seleccionado");
    destination.focus();
}

/**
 * Asigna el callback al boton "aceptar".
 *
 * @param {Function} callback_aceptar - Función a asignar como callback
 */
function set_callback_aceptar(callback_aceptar) {
    callbacks_especiales.aceptar = callback_aceptar;
}

/**
 * Función que se ejecuta cuando se apreta una tecla del teclado  y
 * decide qué callback se llama según si es especial o no.
 *
 * @param {*} data - Elemento de DOM que se presionó.
 */
/* exported click_letra */
function click_letra(target) {
    const es_tecla_con_accion = target.classList.contains(
        "ui-keyboard-actionkey"
    );
    if (es_tecla_con_accion) {
        const accion = target.dataset.accion;
        callbacks_especiales[accion](target);
    } else {
        escribir_letra(target.textContent);
    }
}

/**
 * Le agrega al campo destino el contenido de la tecla.
 *
 * @param {*} letra - Contenido de la tecla que se presionó.
 */
function escribir_letra(letra) {
    const no_escribir_letra =
        destination.hasAttribute("maxLength") &&
        destination.value.length >= destination.maxLength;
    if (no_escribir_letra) return;

    destination.value += letra;
    destination.focus();
    destination.dispatchEvent(new Event("input"));
}

/** A continuación estan los callbacks de las teclas especiales. */

/** Escribe letra espacio (' ') */
/* exported boton_espacio */
function boton_espacio() {
    escribir_letra(" ");
}

/** Escribe letra tilde ('\') */
/* exported boton_tilde */
function boton_tilde() {
    escribir_letra("'");
}

/**
 * Selecciona el tipo de documento.
 *
 * @param {*} target - Elemento html al que se le extrae el texto que contiene.
 */
/* exported seleccionar_documento */
function seleccionar_documento(target) {
    destination.value = target.textContent;
    seleccionar_siguiente();
}

/** Encuentra el siguiente input y le asigna el foco. */
function seleccionar_siguiente() {
    const siguiente = find_next_input(inputs, destination);
    if (siguiente && siguiente.hasAttribute("name")) {
        destination = siguiente;
        destination.focus();
    }
}

/**
 * Encuentra el input anterior y le asigna el foco.
 */
function seleccionar_anterior() {
    var anterior = find_prev_input(inputs, destination);
    if (anterior && anterior.hasAttribute("name")) {
        destination = anterior;
        destination.focus();
    }
}

/**
 * Borra el último caracter del input seleccionado.
 * Si el campo estaba vacio, mueve el foco al campo anterior.
 */
/* exported boton_borrar */
function boton_borrar() {
    if (destination.value.length > 0) {
        destination.value = destination.value.slice(0, -1);
        destination.focus();
        var event = new CustomEvent("borrado");
        destination.dispatchEvent(event);
    } else {
        seleccionar_anterior();
    }
}

/** Resalta le letra asignandole una class css. */
function resaltar_letra(evento) {
    evento.currentTarget.classList.add("resaltado");
}

/** Quita resaltado de todas las letras. */
function desresaltar_letra() {
    document
        .querySelectorAll(".ui-keyboard-button")
        .forEach((tecla) => tecla.classList.remove("resaltado"));
}

/** Emite el sonido de apretar una tecla. */
/* exported sonar_beep */
function sonar_beep(data) {
    beep(data);
}

/** Escribe letra asterisco ('*') */
/* exported seleccionar_asterisco */
function seleccionar_asterisco() {
    apretar_asterisco();
}

/** Escribe letra numeral ('#') */
/* exported seleccionar_numeral */
function seleccionar_numeral() {
    apretar_numeral();
}

/**
 * Contiene el comportamiento cuando se hace foco en un campo:
 * Muestra el tipo de teclado que corresponde, lo marca como seleccionado
 * y adecúa los botones de siguiente/anterior.
 */
const on_focus_in_factory = (inputs) => (evento) => {
    destination = evento.target;
    const ultimo = destination.value.length;

    inputs.forEach((input) => input.classList.remove("seleccionado"));
    destination.classList.add("seleccionado");

    if ("keyboard" in destination.dataset) {
        const keyboard_type = destination.dataset.keyboard;
        patio_teclado[keyboard_type].only();
        document.dispatchEvent(new Event("cambioTeclado"));
    }

    const input_siguiente = find_next_input(inputs, destination);
    const input_anterior = find_prev_input(inputs, destination);
    const botones_aceptar = document.querySelectorAll(
        "div.ui-keyboard-aceptar"
    );
    const botones_siguiente = document.querySelectorAll(
        "div.ui-keyboard-siguiente"
    );
    const botones_anterior = document.querySelectorAll(
        "div.ui-keyboard-anterior"
    );
    const hay_callback_aceptar =
        typeof callbacks_especiales["aceptar"] === "function";

    if (input_siguiente) {
        botones_aceptar.forEach((boton_aceptar) => {
            boton_aceptar.textContent = "Siguiente";
            boton_aceptar.classList.add("ui-keyboard-siguiente");
            boton_aceptar.classList.remove("ui-keyboard-aceptar");
            boton_aceptar.dataset.accion = "siguiente";
        });
    } else if (hay_callback_aceptar) {
        botones_siguiente.forEach((boton_siguiente) => {
            boton_siguiente.textContent = "Aceptar";
            boton_siguiente.classList.add("ui-keyboard-aceptar");
            boton_siguiente.classList.remove("ui-keyboard-siguiente");
            boton_siguiente.dataset.accion = "aceptar";
        });
    }

    if (input_siguiente) {
        botones_siguiente.forEach((boton_siguiente) => {
            boton_siguiente.classList.remove("disabled");
            boton_siguiente.dispatchEvent(new Event("btnSiguienteHabilitado"));
        });
    } else {
        botones_siguiente.forEach((boton_siguiente) => {
            boton_siguiente.classList.add("disabled");
            boton_siguiente.dispatchEvent(
                new Event("btnSiguienteDeshabilitado")
            );
        });
    }

    if (input_anterior) {
        botones_anterior.forEach((boton_anterior) =>
            boton_anterior.classList.remove("disabled")
        );
    } else {
        botones_anterior.forEach((boton_anterior) =>
            boton_anterior.classList.add("disabled")
        );
    }

    evento.target.focus();
    if (ultimo > 0) {
        evento.target.setSelectionRange(ultimo, ultimo);
    }
};

const load_inputs = (inputs) => {
    const on_focus_in = on_focus_in_factory(inputs);
    inputs.forEach((input) => input.classList.add("text"));
    inputs.forEach((input) => input.addEventListener("focusin", on_focus_in));
};

/* Auxiliares */

/**
 * Dado un elemento, retorna el proximo input.
 *
 * @param {Object} elem - Elemento del dom del cual se busca el input siguiente.
 * @param {Object[]} elem - Arreglo de inputs.
 */
function find_next_input(inputs, elem) {
    const input_index = inputs.indexOf(elem);
    if (input_index === -1) return null;
    if (input_index >= inputs.length - 1) return null;
    return inputs[input_index + 1];
}

/**
 * Dado un elemento, retorna el input anterior.
 *
 * @param {Object} elem - elemento del dom del cual se busca el input que lo precede.
 * @param {Object[]} elem - Arreglo de inputs.
 */
function find_prev_input(inputs, elem) {
    const input_index = inputs.indexOf(elem);
    if (input_index <= 0) return null;
    return inputs[input_index - 1];
}

/** Envía al back-end el mensaje "sonido_tecla". */
/* exported sonido_teclado */
function sonido_teclado() {
    send("sonido_tecla");
}

/**
 * Oculta el teclado editando su estilo
 */
/* exported cerrar_teclado */
function cerrar_teclado() {
    document.querySelector("#keyboard").style.display = "none";
}

/**
 * Cierra teclado y quita sus referencias. Necesario cuando se quiere setear
 * otro teclado con su propia configuración particular (distintos inputs,
 * distintos layouts, etc)
 */
/* exported eliminar_teclado */
function eliminar_teclado(elementTeclado) {
    elementTeclado.innerHTML = "";
    patio_teclado = null;
    destination = null;
    inputs = [];
}
