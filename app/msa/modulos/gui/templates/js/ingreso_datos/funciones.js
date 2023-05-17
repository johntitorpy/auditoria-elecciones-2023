/**
 * @namespace js.ingreso_datos.funciones
 */
"use strict";

/**
 * Se dispara cuando se terminó de cargar la pagina.
 */
const document_ready = () => {
    preparar_eventos();
    bind_event_to_click("dragstart", document);
    load_ready_msg();
    asignar_evento(".popup-box", restaurar_foco_invalido, "hideDialogo");
};

ready(document_ready);

const bind_event_to_click = (tipo_evento, element) => {
    element.addEventListener(tipo_evento, (event) => {
        event.target.click();
    });
};

/**
 * Envía al backend la mesa y pin ingresada por el usuario
 */
function enviar_mesaypin() {
    var nro_mesa = document.getElementsByName("nro_mesa")[0].value;
    var nro_pin = obtener_pin();

    mensaje_validando_mesa();

    setTimeout(function () {
        if (validar_pin(nro_pin)) {
            var data = {
                mesa: nro_mesa,
                pin: nro_pin.substr(0, nro_pin.length - 1),
            };
            send("recibir_mesaypin", data);
        }
    }, 200);
}


//Funciones que envian datos
function enviar_id_mesa_y_pin(){
    // Envía al backend la mesa y pin ingresada por el usuario
    var nro_mesa = document.getElementsByName("nro_mesa")[0].value;
    var id_unico = document.getElementsByName("id_unico")[0].value;
    var nro_pin = obtener_pin();
    mensaje_validando_mesa();

    setTimeout(
        function(){
            if(validar_pin(nro_pin)) {
                var data = {
                    "id_unico": id_unico,
                    "mesa": nro_mesa,
                    "pin": nro_pin.substr(0, nro_pin.length - 1)
                };
                send("recibir_id_mesa_y_pin", data);
            }

        },
        200);
}

/**
 * Envía al backend la hora y los datos de las autoridades de mesa. Obtenemos los cargos que hay en la pantalla.
 */
function enviar_datospersonales() {
    const elem_cargos = Array.from(document.querySelectorAll(".cargo"));

    // Ejemplo: ["presidente", "suplente"]
    const cargos = elem_cargos.map((elem) => elem.dataset.cargo);

    // Ejemplo: ["DNI", "LE", "LC"]
    const tipodocs = constants.tipo_doc.map(([index, tipo_doc]) => tipo_doc);

    // Devuelve un arreglo donde cada item contiene los datos de una autoridad.
    // Estructura: [ ["nombre", "apellido", "posicion_tipodoc", "dni"], [...], ... ]
    const autoridades = cargos.map((cargo) => {
        return Array.from(document.querySelectorAll(`#${cargo} input`)).map(
            (input) => {
                const valor = input.value;
                if (!valor) return "";
                const input_name = input.name.slice(cargo.length + 1);
                if (input_name == "tipo_documento")
                    return tipodocs.indexOf(valor).toString();
                return valor;
            }
        );
    });

    // Obtenemos hora
    var hora = {
        horas: filterInt(document.querySelector("input[name='hora']").value),
        minutos: filterInt(
            document.querySelector("input[name='minutos']").value
        ),
    };

    var data = {
        hora: hora,
        autoridades: autoridades,
    };

    send("recibir_datospersonales", data);
}
/**
 * Renderiza un template de pop mostrando mensaje de error referido a la mesa y al pin.
 */
function msg_mesa_y_pin_incorrectos() {
    const generador_html = (template_popup) => {
        const mensaje = constants.i18n.mesa_pin_incorrectos;
        const datos_validos = inputs_son_validos(
            Array.from(document.querySelectorAll(".mesaypin input"))
        );
        const template_data = {
            alerta: mensaje,
            btn_aceptar: true,
            btn_cancelar: false,
            clase_aceptar: !datos_validos ? "error-validacion" : false,
        };
        return template_popup(template_data);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}

function msg_ubicacion_incorrecta(){
    const mensaje = constants.i18n.ubicacion_incorrecta +
        ": no existe una mesa con el ID y número de mesa ingresados";

    const template_data = {
        alerta: mensaje,
        btn_aceptar: true,
        btn_cancelar: false
    };
    cargar_dialogo_default(template_data);
}

/**
 * Funcion que avisa un mensaje de error de validacion
 * @param mensaje - Mensaje de error
 */
function msg_error_validacion(mensaje) {
    const generador_html = (template_popup) => {
        const datos_validos = inputs_son_validos(
            Array.from(document.querySelectorAll(".mesaypin input"))
        );
        const template_data = {
            alerta: mensaje,
            btn_aceptar: true,
            btn_cancelar: false,
            clase_aceptar: "error-validacion",
        };
        return template_popup(template_data);
    };
    return promise_popup("popup", "partials/popup", generador_html);
}
/**
 * Valida el pin y si es correcto se notifica al backend la confirmación del ingreso, caso contrario, se muestra un mensaje al usuario.
 */
function aceptar_mesa_y_pin() {
    const inputs = Array.from(document.querySelectorAll(".mesaypin input"));
    const inputs_validos = inputs_son_validos(inputs);
    const pin = obtener_pin();
    const pin_valido = validar_pin(pin);
    const datos_validos = inputs_validos && pin_valido;
    if (!datos_validos) {
        cargar_dialogo("msg_mesa_y_pin_incorrectos");
        return;
    }
    send("msg_confirmar_ingreso");
}

/**
 * Dado un arreglo de inputs devuelve true si todos los valores son válidos.
 * Para hacer esto se usa la función checkValidity() la api del DOM para los inputs.
 * @param {Object[]} inputs - Arreglo que contiene inputs del DOM.
 * @returns {boolean} - True si todos los inputs tienen valores validos.
 */
const inputs_son_validos = (inputs) => {
    return inputs.reduce((booleano_acumulado, actual_input) => {
        return booleano_acumulado && actual_input.checkValidity();
    }, true);
};
/**
 * Valida datos personales.
 *
 * @todo separar toda la lógica interna a este método
 * en un modulo de js aparte de funciones.js.
 */
function aceptar_datos_personales() {
    /** FUNCIONES */
    /**
     * Devuelve true si el input solo tiene un caracter.
     * @param  {object} input - Objeto del dom de tipo input.
     * @returns {boolean} - Verdadero si el input solo tiene un caracter.
     */
    const input_tiene_un_caracter = (input) => input.value.trim().length === 1;

    /**
     * Devuelve true si el input está vacio.
     * @param  {object} input - Objeto del dom de tipo input.
     * @returns {boolean} - Verdadero si el input está vacio.
     */
    const input_esta_vacio = (input) => input.value.length === 0;

    /**
     * Devuelve true si el input solo tiene espacios vacios.
     * @param  {object} input - Objeto del dom de tipo input.
     * @returns {boolean} - Verdadero si el input solo tiene espacios vacios.
     */
    const tiene_solo_espacios = (input) => Boolean(input.value.match(/^\s+$/));

    const tiene_mas_de_n_caracteres = (n) => (input) => input.value.length > n;
    const tiene_mas_de_8_caracteres = tiene_mas_de_n_caracteres(8);
    const tiene_al_menos_1_caracter = tiene_mas_de_n_caracteres(0);

    /**
     * @function
     * @description Devuelve un conjunto de inputs por cada formulario de autoridad
     * por ejemplo: [<input>, <input>,...] donde conjunto pertenece a la autoridad recibida
     * por parametro (presidente, suplente, suplente 2, etc)
     * Además se filtran los inputs de tipo_documento.
     * @param {Object} - Formulario de la autoridad (Ejemplo: <form id="presidente">).
     * @returns {Object[]} - Arreglo donde cada item es un arreglo con inputs de la autoridad.
     */
    const inputs_de_autoridad = (autoridad) => {
        return Array.from(
            autoridad.querySelectorAll("input:not(.tipo_documento)")
        );
    };

    /** FIN FUNCIONES */

    /** CAMPOS DEL DOM */

    const inputs_excepto_nro_doc = Array.from(
        document.querySelectorAll(
            ".nombre-autoridades input:not(.nro_documento)"
        )
    );
    const inputs_nro_doc = Array.from(
        document.querySelectorAll(".nombre-autoridades input.nro_documento")
    );

    const input_hora = document.querySelector("input[name='hora']");
    const input_minutos = document.querySelector("input[name='minutos']");

    // Devuelve por ejemplo: [<form id="presidente">, <form id="suplente">]
    const forms_autoridades = Array.from(
        document.querySelectorAll("form.autoridad")
    );

    /** FIN CAMPOS DEL DOM */

    // Valida campos de autoridades
    const datos_invalidos = !inputs_son_validos(inputs_excepto_nro_doc);
    const largo_invalido = inputs_excepto_nro_doc.some(input_tiene_un_caracter);
    const campo_vacio = inputs_excepto_nro_doc.some(tiene_solo_espacios);
    const documentos_invalidos = !inputs_son_validos(inputs_nro_doc);
    const documentos_numeros_invalidos = inputs_nro_doc.some(
        tiene_mas_de_8_caracteres
    );

    // Valida campos de hora y minutos
    const hora_vacia = !(input_hora.value && input_minutos.value);
    const hora_invalida = !(
        inputs_son_validos([input_hora, input_minutos]) &&
        input_hora.value !== "1"
    );
    // usa xor porque se asume que si ningun campo de hora está cargado entonces la hora
    // no está incompleta, es directamente inválida.
    const hora_incompleta = !input_hora.value ^ !input_minutos.value;

    // Valida campos de autoridad, cada una como un conjunto.

    // Autoridades que tengan al menos un dato (con que haya un caracter en un input es suficiente)
    const autoridades_con_datos_cargados = forms_autoridades
        .map(inputs_de_autoridad)
        .filter((inputs_autoridad) =>
            inputs_autoridad.some(tiene_al_menos_1_caracter)
        );

    // Dentro de las autoridades que se empezaron a cargar, las que tienen campos vacios
    // Esto puede ser, por ejemplo, cuando se cargó el nombre del suplente pero no su apellido.
    const autoridades_con_datos_pero_incompletos = autoridades_con_datos_cargados.filter(
        (inputs_autoridad) => inputs_autoridad.some(input_esta_vacio)
    );
    const hay_autoridades_cargadas = autoridades_con_datos_cargados.length > 0;
    const hay_autoridades_incompletas =
        autoridades_con_datos_pero_incompletos.length > 0;

    /**
     * @todo refactorear esta lógica, puede hacerse de manera más sencilla
     * iterando un arreglo de jsons en lugar de manejar booleanos sueltos.
     */
    //Si esta todo bien, confirma ingreso
    if (
        !datos_invalidos &&
        !documentos_invalidos &&
        !documentos_numeros_invalidos &&
        !hay_autoridades_incompletas &&
        !largo_invalido &&
        !campo_vacio &&
        hay_autoridades_cargadas &&
        !hora_incompleta &&
        !hora_invalida &&
        !hora_vacia
    ) {
        send("msg_confirmar_ingreso");
    } else {
        var mensaje = "";
        var error = constants.mensajes_error;
        if (hora_vacia) {
            mensaje += "<li>" + error.hora_vacia + "</li>";
        }
        if (hora_incompleta) {
            mensaje += "<li>" + error.hora_incompleta + "</li>";
        }
        if (hora_invalida) {
            mensaje += "<li>" + error.hora_invalida + "</li>";
        }
        if (!hay_autoridades_cargadas) {
            mensaje += "<li>" + error.debe_cargar_autoridad + "</li>";
        }
        if (largo_invalido) {
            mensaje += "<li>" + error.largo_invalido + "</li>";
        }
        if (campo_vacio) {
            mensaje += "<li>" + error.campo_vacio + "</li>";
        }
        if (datos_invalidos) {
            mensaje += "<li>" + error.autoridades_invalidas + "</li>";
        }
        if (documentos_invalidos) {
            mensaje += "<li>" + error.documentos_invalidos + "</li>";
        }
        if (documentos_numeros_invalidos) {
            mensaje += "<li>" + error.documentos_numeros_invalidos + "</li>";
        }
        if (hay_autoridades_incompletas) {
            mensaje += "<li>" + error.autoridades_incompletas + "</li>";
        }

        cargar_dialogo_default({ pregunta: mensaje, btn_aceptar: true }).then(
            () => {
                document
                    .querySelector(".mensaje-popup")
                    .classList.add("lista-popup");
            }
        );
    }
}
/**
 * Muestra/oculta un tooltip de ayuda al usuario, el cual se ubica al costado del teclado,
 * en función de si el elemento input tiene el atributo "data-tooltip" o no.
 * Esta función se ejecuta cuando el usuario se posa en un nuevo input.
 * Cuando eso sucede la variable global "destination" toma el valor del
 * input y en esta función se consulta si el valor de "data-tooltip" es true o no.
 */
const mostrar_tooltip = (evento) => {
    /**@todo: Los módulos no deberian poder acceder directamente a la variable destination
     * ya que es una variable interna del teclado (ver teclado/base.js). Este código debe
     * ser refactorizado a futuro.
     */
    const tiene_tooltip =
        destination && destination.dataset && destination.dataset.tooltip;
    const ingreso = document.querySelector(".ingreso");
    const ingreso_tooltip = document.querySelector(".ingreso + .tooltip");
    if (tiene_tooltip) {
        ingreso.classList.add("con-tooltip");
        ingreso_tooltip.style.display = "block";
    } else {
        ingreso.classList.remove("con-tooltip");
        ingreso_tooltip.style.display = "none";
    }
};

/* Funciones auxiliares */

/**
 * Obtiene un frgmento del pin de cada input correspondiente, lo concatena y lo devuelve.
 */
function obtener_pin() {
    var campos = document.querySelectorAll("[name^=nro_pin]");
    var pin = "";
    for (var i = 0; i < campos.length; i++) {
        pin = pin.concat(campos[i].value);
    }
    return pin;
}

/**
 * Valida el pin ingresado por el usuario.
 * @param  {string} nro_pin
 */
function validar_pin(nro_pin) {
    var suma = 0;
    var pin = nro_pin.split("");
    var digito_verificador = pin.pop();
    for (var letra in pin) {
        suma += pin[letra].charCodeAt();
    }
    const caracter = suma % 10;
    return caracter == Number(digito_verificador);
}

/**
 * @function
 * @description Valida la hora y si es correcta pasa al input siguiente llamando al método ``seleccionar_siguiente``.
 * @param  {event} event
 */
const on_campo_horario = (modulo, camposVisitados = []) => () => {
    const activo = document.activeElement;
    agregarVisita(activo.name);
    const { hora, minutos } = validarCamposHorarios(
        modulo,
        camposVisitados,
        activo
    );
    autopasarCampoDeHorario(hora, minutos, () => seleccionar_siguiente());

    function agregarVisita(nombre) {
        if (!camposVisitados.includes(nombre)) camposVisitados.push(nombre);
    }
};

/**
 * Hace una validación y si es correcta pasa al input siguiente llamando a la función ``seleccionar_siguiente``.
 * @param  {event} event
 */
function autopasa_campo_datos(event) {
    const current_value = event.currentTarget.value;
    const maxlength = event.currentTarget.getAttribute("maxlength");
    if (current_value.length >= maxlength) {
        seleccionar_siguiente();
    }
}

/**
 * Deshabilita el evento ``keydown``
 */
function deshabilitar_teclado() {
    Array.from(
        document.querySelectorAll(
            ".contenedor-datos input, .contenedor-datos select"
        )
    ).forEach((i) =>
        i.addEventListener("keydown", (event) => event.preventDefault())
    );
}

/**
 * Escribe el contenido de ``data`` en un elemento html.
 * @param  {string} data
 */
function set_mensaje(data) {
    document.querySelector(".contenedor-texto h1").innerHTML = data;
}

/**
 * Toma los teclados de ``lista_teclados`` y los inicializa, esto es, les asigna los eventos correspondientes (llamando a la funcion :meth:`js.base.load_teclados`)
 *
 * @param  {string[]} lista_teclados
 *
 * @param  {function} callback_aceptar
 */
const inicializar_teclado = (lista_teclados, callback_aceptar) => {
    const elementTeclado = document.querySelector("#keyboard");
    eliminar_teclado(elementTeclado);
    return load_teclados(
        elementTeclado,
        document.querySelectorAll("input[type='text']"),
        {
            layout: lista_teclados,
            callback_finish: callback_aceptar,
        }
    );
};

/**
 * Envía el mensaje 'salir' al backend.
 */
function salir() {
    send("salir");
}

/**
 * Asigna eventos :meth:`js.apertura.funciones.scroll_up` y :meth:`js.apertura.funciones.scroll_down` a elementos de scroll.
 * A tener en cuenta: Los scrolls pueden no estar en el DOM por lo que es necesario chequear
 * que existan antes de asignarle comportamiento.
 */
function bindear_scrolls() {
    const scroll_arriba = document.getElementById("_btn_scroll_arriba");
    const scroll_abajo = document.getElementById("_btn_scroll_abajo");
    if (scroll_arriba) scroll_arriba.addEventListener("click", scroll_up);
    if (scroll_abajo) scroll_arriba.addEventListener("click", scroll_abajo);
}

/**
 * Implementación del evento que desliza la página hacia arriba.
 */
function scroll_up() {
    const elem = document.querySelector(".nombre-autoridades");
    const pos = elem.scrollTop;
    elem.scrollTop = pos - 50;
}

/**
 * Implementación del evento que desliza la página hacia abajo.
 */
function scroll_down() {
    const elem = document.querySelector(".nombre-autoridades");
    const pos = elem.scrollTop;
    elem.scrollTop = pos + 50;
}

/**
 * Valida si string ``value`` es un entero válido
 *  @param  {string} value
 */
function esEnteroValido(value) {
    return /^(\-|\+)?([0-9]+|Infinity)$/.test(value);
}

/**
 * Devuelve entero si ``value`` es entero, caso contrario devuelve NaN.
 *  @param  {string} value
 */
function filterInt(value) {
    return esEnteroValido(value) ? Number(value) : NaN;
}
