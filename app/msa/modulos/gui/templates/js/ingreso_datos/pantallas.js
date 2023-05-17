/**
 * @namespace js.ingreso_datos.pantallas
 */
"use strict";

/**
 * Muestra mensaje de validación de PIN.
 */
function mensaje_validando_mesa() {
    mostrar_mensaje("Validando PIN...", null, null, true);
}

/**
 * Renderiza pantalla de ingreso de acta.
 * @param {json} data
 */
function pantalla_ingresoacta(data) {
    var w = window.outerWidth;
    hide_all();
    const promise_ingreso_acta = fetch_template(
        "ingreso_acta",
        "pantallas/ingreso_datos"
    );
    const promise_popup = fetch_template("popup", "pantallas/ingreso_datos");
    Promise.all([promise_ingreso_acta, promise_popup]).then(
        ([template_ingreso_acta, template_popup]) => {
            const template_data = {
                mensaje: data.mensaje,
            };
            const html_pantallas = template_ingreso_acta(template_data);
            const html_popup = template_popup();

            document.querySelector(
                ".contenedor-datos"
            ).innerHTML = html_pantallas;
            document.querySelector(".popup-box").innerHTML = html_popup;
            const btn_salir_accesibilidad = document.querySelector(
                "#accesibilidad #btn_salir"
            );
            if (btn_salir_accesibilidad) {
                btn_salir_accesibilidad.addEventListener("click", salir);
            }
            hide_elements(".barra-titulo");
            hide_dialogo();
            show_elements("#contenedor_izq");
            show_elements("#contenedor_opciones");
            show_elements(".contenedor-datos");

            //const img_svg = decodeURIComponent(data.imagen_acta);
            if (w < 1400) {
                var img_svg =
                    "<img style='margin-top:-10px' src='img/apertura_izq.png'/>";
            } else {
                var img_svg =
                    "<img style='margin-top:-10px' src='img/apertura.png'/>";
            }
            const cont = document.querySelector(".acta-izq");
            cont.innerHTML = img_svg;
        }
    );
}

/**
 * Renderiza pantalla de mesa y pin
 * @param {Array} data
 */
function pantalla_mesaypin(data) {
    const teclado_fisico = data[0];
    const callback_aceptar = data[1];
    const mesa = data[2];
    const mostrar_imagen = data[3];
    const promise_mesapin = fetch_template(
        "mesa_y_pin",
        "pantallas/ingreso_datos"
    );
    const promise_teclado = fetch_template(
        "teclado",
        "pantallas/ingreso_datos"
    );
    const promise_popup = fetch_template("popup", "pantallas/ingreso_datos");
    Promise.all([promise_mesapin, promise_teclado, promise_popup]).then(
        ([template_mesapin, template_teclado, template_popup]) => {
            const template_data = {
                pattern_mesa: "[0-9]*[F|M|X]?",
                pattern_pin: "([A-Z 0-9]{0,8})",
                mesa: mesa,
                mostrar_imagen: mostrar_imagen,
                mostrar_tooltip:
                    !mostrar_imagen ||
                    (constants.realizar_apertura &&
                        mostrar_imagen &&
                        constants.usa_login_desde_inicio),
            };
            template_data.af_mesa = mesa === "";
            template_data.af_pin = mesa !== "";
            Handlebars.registerPartial("teclado", template_teclado);
            const html_pantallas = template_mesapin(template_data);
            const html_popup = template_popup();
            document.querySelector(
                ".contenedor-datos"
            ).innerHTML = html_pantallas;
            document.querySelector(".popup-box").innerHTML = html_popup;

            document
                .querySelector(".barra-titulo p")
                .setAttribute("id", "_txt_ingrese_mesa_y_pin");
            place_text(constants.i18n);
            document
                .querySelector(".btn-cancelar p")
                .setAttribute("id", "_txt_cancelar");
            document
                .querySelector(".btn-aceptar p")
                .setAttribute("id", "_txt_aceptar");
            inicializar_teclado(["qwerty"], window[callback_aceptar]).then(
                () => {
                    place_text(constants.i18n);
                    place_text(constants.encabezado);
                }
            );

            hide_all();
            show_elements("#contenedor_izq");
            show_elements(".barra-titulo");
            show_elements(".contenedor-datos", function () {
                if (!teclado_fisico) {
                    deshabilitar_teclado();
                }
            });

            Array.from(
                document.querySelectorAll("input.nro_pin")
            ).forEach((i) => i.addEventListener("input", autopasa_campo_datos));
        }
    );
}

/**
 * Renderiza pantalla de id, mesa y pin
 * @param {Array} data
 */
function pantalla_id_mesa_y_pin(data) {
    const teclado_fisico = data[0];
    const callback_aceptar = data[1];
    const mesa = data[2];
    const mostrar_imagen = data[3];
    const promise_idmesapin = fetch_template(
        "id_mesa_y_pin",
        "pantallas/ingreso_datos"
    );
    const promise_teclado = fetch_template(
        "teclado",
        "pantallas/ingreso_datos"
    );
    const promise_popup = fetch_template("popup", "pantallas/ingreso_datos");
    Promise.all([promise_idmesapin, promise_teclado, promise_popup]).then(
        ([template_idmesapin, template_teclado, template_popup]) => {
            const template_data = {
                pattern_id_unico: "[0-9]{0,5}",
                pattern_mesa: "[0-9]*[F|M|X]?",
                pattern_pin: "([A-Z 0-9]{0,8})",
                mesa: mesa,
                mostrar_imagen: mostrar_imagen,
                mostrar_tooltip:
                    !mostrar_imagen ||
                    (constants.realizar_apertura &&
                        mostrar_imagen &&
                        constants.usa_login_desde_inicio),
            };
            Handlebars.registerPartial("teclado", template_teclado);
            console.log(template_idmesapin)
            const html_pantallas = template_idmesapin(template_data);
            const html_popup = template_popup();
            document.querySelector(
                ".contenedor-datos"
            ).innerHTML = html_pantallas;
            document.querySelector(".popup-box").innerHTML = html_popup;

            document
                .querySelector(".barra-titulo p")
                .setAttribute("id", "_txt_ingrese_mesa_y_pin");
            place_text(constants.i18n);
            document
                .querySelector(".btn-cancelar p")
                .setAttribute("id", "_txt_cancelar");
            document
                .querySelector(".btn-aceptar p")
                .setAttribute("id", "_txt_aceptar");
            inicializar_teclado(["qwerty"], window[callback_aceptar]).then(
                () => {
                    place_text(constants.i18n);
                    place_text(constants.encabezado);
                }
            );

            hide_all();
            show_elements("#contenedor_izq");
            show_elements(".barra-titulo");
            show_elements(".contenedor-datos", function () {
                if (!teclado_fisico) {
                    deshabilitar_teclado();
                }
            });

            document.querySelector("input[name=id_unico]").addEventListener("focus", function () {
                document.getElementById("texto_ayuda").innerText = constants.i18n["ayuda_id_unico_mesa"]
            });

            document.querySelector("input[name=nro_mesa]").addEventListener("focus", function () {
                document.getElementById("texto_ayuda").innerText = constants.i18n["ayuda_numero_mesa"]
            });

            document.querySelector("input.nro_pin").addEventListener("focus", function () {
                document.getElementById("texto_ayuda").innerText = constants.i18n["ayuda_numero_pin"]
            });

            document.querySelector("input[name=id_unico]").focus();

            Array.from(
                document.querySelectorAll("input.nro_pin")
            ).forEach((i) => i.addEventListener("input", autopasa_campo_datos));
        }
    );
}

/**
 * Renderiza pantalla de datos personales.
 * @param {json} data
 */
function pantalla_datospersonales(data) {
    let datos_precargados = false;
    const teclado_fisico = data.teclado_fisico;
    const pattern_validacion_hora = data.pattern_validacion_hora;

    const promise_datospersonales = fetch_template(
        "datos_personales",
        "pantallas/ingreso_datos"
    );
    const promise_teclado = fetch_template(
        "teclado",
        "pantallas/ingreso_datos"
    );
    const promise_popup = fetch_template("popup", "pantallas/ingreso_datos");

    Promise.all([promise_teclado, promise_popup, promise_datospersonales]).then(
        ([template_teclado, template_popup, template_datospersonales]) => {
            hide_all();
            if (data.modulo === "escrutinio") {
                document.addEventListener("cambioTeclado", mostrar_tooltip);
            }

            const autoridades = [
                {
                    cargo: constants.i18n.titulo_autoridad_1,
                    id_cargo: constants.i18n.titulo_autoridad_1
                        .toLowerCase()
                        .replace(/ /g, "_"),
                },
            ];

            if (constants.cantidad_suplentes > 1) {
                for (let i = 1; i <= constants.cantidad_suplentes; i++) {
                    autoridades.push({
                        cargo: constants.i18n.titulo_autoridad_2 + " " + i,
                        id_cargo:
                            constants.i18n.titulo_autoridad_2
                                .toLowerCase()
                                .replace(/ /g, "_") + i,
                    });
                }
            } else if (constants.cantidad_suplentes == 1) {
                autoridades.push({
                    cargo: constants.i18n.titulo_autoridad_2,
                    id_cargo: constants.i18n.titulo_autoridad_2
                        .toLowerCase()
                        .replace(/ /g, "_"),
                });
            }

            let tipo_doc = [];
            for (let j = 0; j < constants.tipo_doc.length; j++) {
                tipo_doc.push(constants.tipo_doc[j][1]);
            }

            const template_data = {
                autoridades: autoridades,
                scroll: constants.cantidad_suplentes > 2,
                tipo_doc_default: tipo_doc[0],
                disabled_default: false,
                regex_hora: pattern_validacion_hora,
                mostrar_tooltip: data.modulo === "escrutinio",
            };

            Handlebars.registerPartial("teclado", template_teclado);
            const html_pantallas = template_datospersonales(template_data);
            const html_popup = template_popup();
            document.querySelector(
                ".contenedor-datos"
            ).innerHTML = html_pantallas;
            document.querySelector(".popup-box").innerHTML = html_popup;

            //Rellena los datos en los campos
            if (data.hora) {
                datos_precargados = true;
                document.querySelector("input[name='hora']").value =
                    data.hora.horas;
                document.querySelector("input[name='minutos']").value =
                    data.hora.minutos;
            }

            if (data.autoridades && data.autoridades.length) {
                datos_precargados = true;
                let campo;
                let dato;
                for (let j = 0; j < data.autoridades.length; j++) {
                    for (let valor in data.autoridades[j]) {
                        try {
                            dato = data.autoridades[j][valor].replace(
                                new RegExp("&#39;", "g"),
                                "'"
                            );
                        } catch (TypeError) {
                            dato = data.autoridades[j][valor];
                        }

                        campo = document.querySelector(
                            `[name='${autoridades[j].id_cargo}_${valor}']`
                        );
                        campo.removeAttribute("disabled");
                        if (valor == "tipo_documento" && !isNaN(dato)) {
                            campo.value = tipo_doc[dato];
                        } else {
                            campo.value = dato;
                        }
                    }
                }
            }

            document
                .querySelector(".barra-titulo p")
                .setAttribute("id", "_txt_ingrese_datos_personales");
            inicializar_teclado(
                ["alpha", "num", "docs", "mensaje"],
                window[data.callback_aceptar]
            ).then(() => {
                const primer_input = inputs[0];
                const ultimo_input = inputs.slice(-1)[0];
                if (datos_precargados && !data.foco_hora) {
                    ultimo_input.focus();
                } else {
                    primer_input.focus();
                }
                place_text(constants.i18n);
                place_text(constants.encabezado);
            });
            show_elements(".barra-titulo");
            show_elements(".contenedor-datos", function () {
                if (!teclado_fisico) {
                    deshabilitar_teclado();
                }
            });

            if (template_data.mostrar_tooltip) {
                //var img_svg = decodeURIComponent(data.imagen_acta);
                var img_svg =
                    "<img src='img/recuento.png' style='height:250px; margin-left: 30px'/>";
                var cont = document.querySelector("#svg_cierre");
                cont.innerHTML = img_svg;
            }

            bindear_scrolls();
            const modulo_actual =
                data.modulo === "escrutinio" ? data.modulo : "apertura";
            const inputs = Array.from(document.getElementsByTagName("input"));
            const inputs_hora_minutos = Array.from(
                document.querySelectorAll(
                    "input[name='hora'], input[name='minutos']"
                )
            );

            const accion_en_campo_horario = on_campo_horario(modulo_actual);

            inputs_hora_minutos.forEach((i) =>
                i.addEventListener("input", accion_en_campo_horario)
            );

            inputs_hora_minutos.forEach((i) =>
                i.addEventListener("borrado", accion_en_campo_horario)
            );

            Array.from(
                document.querySelectorAll(
                    'input[name$="_apellido"], input[name$="_nombre"], input[name$="_nro_documento"]'
                )
            ).forEach((i) => i.addEventListener("input", autopasa_campo_datos));
        }
    );
}

function pantalla_confirmacion_apertura(data) {
    /* Muestra la pantalla de confirmacion de la apertura
     *
     * Argumentos:
     *     data -- json con las claves que usa handlebars para rellenar el template
     */
    fetch_template("confirmacion_apertura", "pantallas/ingreso_datos").then(
        (template_confirmacion_apertura) => {
            // armamos la pantalla.
            const html_pantallas = template_confirmacion_apertura(data);
            document.querySelector(".contenedor-confirmacion").innerHTML = html_pantallas;
            // hookeamos los eventos
            append_click_action(".aceptar", confirmar_action(true))
            append_click_action(".cancelar", confirmar_action(false))
            // aplicamos la internacionalizacion
            place_text(constants.i18n);
            // mostramos la pantalla
            document.querySelector(".contenedor-confirmacion").style.display = "block";
        }
    );
}

const append_click_action = (
    selector,
    action
) => Array.from(
    document.querySelectorAll(selector)
).map(
    element => element.addEventListener(
        "click",
        () => action()
    )
)

const confirmar_action = (aceptar = true) => () => send(
    "msg_confirmar_apertura",
    aceptar
)
