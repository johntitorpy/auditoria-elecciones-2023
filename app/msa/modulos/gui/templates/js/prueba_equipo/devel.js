debug_toolbar_loaded = false;

function create_debug_toolbar() {
    var opciones = $("#barra_opciones:visible");
    if (
        (opciones.is(":visible") || constants.asistida) &&
        !debug_toolbar_loaded
    ) {
        debug_toolbar_loaded = true;
        var toolbar = $(
            "<div id='debug_toolbar' style='clear:both;background:#EEEEEE;border:solid 1px;'></div>"
        );
        $("body").append(toolbar);

        if (!constants.asistida) {
            boton_verificar();
            select_ubicaciones();
            crear_select_grilla();
            $("#debug_toolbar").on(
                "click",
                "#debug_previsualizacion",
                _previsualizar_voto
            );
            $("#debug_toolbar").on("click", "#debug_verif", verificar_voto);
            $("#debug_toolbar").on("click", "#debug_confirmacion", () =>
                _cargar_confirmacion(_seleccion_mock())
            );
            $("#debug_toolbar").on(
                "click",
                "#debug_overflow",
                verificar_overflow
            );
            $("#debug_toolbar").on("click", "#desaparecer", click_desaparecer);
            $("#debug_toolbar").on(
                "click",
                "#debug_insertar",
                insercion_boleta
            );
            $("#debug_toolbar").on("click", "#debug_menu", mostrar_menu_salida);
            $("#debug_toolbar").on(
                "change",
                "#select_ubicaciones select",
                cambiar_ubicacion
            );
            $("#debug_toolbar").on(
                "change",
                "#template_selector select",
                cambiar_template_debug
            );
        } else {
            setTimeout(function () {
                var estilos =
                    'style="float:right;padding:10px;border:solid 1px;margin:0px 5px;background:#EEEEEE;"';
                var boton = $(
                    '<div id="debug_sel_asistida" ' +
                        estilos +
                        ">Elegir y esperar</div>"
                );
                $("#debug_toolbar").append(boton);
                var boton = $(
                    '<div id="debug_fullsel_asistida" ' +
                        estilos +
                        ">Elegir y pasar</div>"
                );
                $("#debug_toolbar").append(boton);
                crear_select_asistida();
                $("#debug_toolbar").on(
                    "click",
                    "#debug_fullsel_asistida",
                    fullelegir_candidato_asistida
                );
                $("#debug_toolbar").on(
                    "click",
                    "#debug_sel_asistida",
                    elegir_candidato_asistida
                );
            }, 4000);
        }
    }
}

function crear_select_asistida() {
    if ($("#template_opcion_asistida").length) return;
    let html_div =
        '<div id="template_opcion_asistida" style="float:right"><select id="select_opcion_asistida"></select></div>';
    let body = $("#debug_toolbar");
    body.html(body.html() + html_div);
}

function populate_select_asistida() {
    const select = $("#template_opcion_asistida select");
    select[0].innerHTML = "";
    for (var i = 1; i < 51; i++) {
        select.append($("<option></option>").attr("value", i).text(i));
    }
}

function fullelegir_candidato_asistida(event) {
    document.getElementById("hidden_input").value = document.getElementById(
        "select_opcion_asistida"
    ).value;
    console.log(
        "Elegido de asistida",
        document.getElementById("hidden_input").value
    );
    apretar_numeral();
    apretar_numeral();
}

function elegir_candidato_asistida(event) {
    document.getElementById("hidden_input").value = document.getElementById(
        "select_opcion_asistida"
    ).value;
    console.log(
        "Elegido de asistida",
        document.getElementById("hidden_input").value
    );
    apretar_numeral();
}

function crear_select_grilla() {
    if ($("#template_selector").length) return;
    var html_div =
        '<div id="template_selector" style="float:right"><select></select></div>';
    var body = $("#debug_toolbar");
    body.html(body.html() + html_div);
}

function populate_select(numeros_templates) {
    var select = $("#template_selector select");
    select[0].innerHTML = "";
    $.each(numeros_templates, function (_, numero) {
        select.append(
            $("<option></option>").attr("value", numero).text(numero)
        );
    });
}

function cambiar_template_debug(event) {
    const opciones = Array.from(
        document.querySelectorAll(`.${contenedor_items_grilla_classname()}`)
    );
    const clases = opciones.reduce(
        (clases_acumuladas, opcion) =>
            clases_acumuladas.concat(Array.from(opcion.classList)),
        []
    );
    const clases_sin_repetidas = Array.from(new Set(clases));
    const clases_a_remover = clases_sin_repetidas.filter((clase) =>
        clase.startsWith(clase_grilla_prefix())
    );
    opciones.forEach((opcion) => {
        opcion.classList.remove(...clases_a_remover);
        opcion.classList.add(nombre_clase(event.target.value));
    });

    if (en_confirmacion()) homogeneizar_tarjetas_confirmacion();

    function nombre_clase(valor) {
        return `${clase_grilla_prefix()}${valor}`;
    }
}

function devel_tools_callback() {
    create_debug_toolbar();
    actualizar_valor_select();
}

function actualizar_valor_select() {
    var contenedor = $(`.${contenedor_items_grilla_classname()}:visible`);
    const do_actualizar = contenedor.is(":visible") && !select_grilla_is_open();
    if (!do_actualizar) return;
    constants.asistida
        ? populate_select_asistida()
        : populate_select(
              en_confirmacion()
                  ? constants.numeros_templates_confirmacion
                  : constants.numeros_templates
          );
    select_template_valor_inicial();
}

function click_desaparecer() {
    $("#debug_toolbar").hide();
    setTimeout(function () {
        $("#debug_toolbar").show();
        return false;
    }, 5000);
}

function boton_verificar() {
    if (!$("#debug_verif").length) {
        var estilos =
            'style="float:right;padding:10px;border:solid 1px;margin:0px 5px;background:#EEEEEE;"';
        var boton = $('<div id="desaparecer" ' + estilos + ">X</div>");
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_previsualizacion" ' +
                estilos +
                ">Previsualizar Voto</div>"
        );
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_verif" ' + estilos + ">Verificar Voto</div>"
        );
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_insertar" ' + estilos + ">Pantalla Inserción</div>"
        );
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_menu" ' + estilos + ">Apoyar Credencial</div>"
        );
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_overflow" ' + estilos + ">Verificar Overflow</div>"
        );
        $("#debug_toolbar").append(boton);
        var boton = $(
            '<div id="debug_confirmacion" ' + estilos + ">Confirmacion</div>"
        );
        $("#debug_toolbar").append(boton);
    }
}

function select_ubicaciones() {
    var template_selector = $("#select_ubicaciones");
    if (!template_selector.length) {
        var queryDict = {};
        location.search
            .substr(1)
            .split("&")
            .forEach(function (item) {
                queryDict[item.split("=")[0]] = item.split("=")[1];
            });
        if (typeof queryDict.ubic == "undefined") {
            queryDict.ubic = constants.cod_datos;
        }
        var html_div =
            '<div id="select_ubicaciones" style="float:right"><select id="ubicaciones"></select></div>';
        var body = $("#debug_toolbar");
        body.append(html_div);
        var select = $("#select_ubicaciones select");
        $.each(constants.ubicaciones, function (iter, ubic) {
            var elem = $("<option></option>")
                .attr("value", ubic[0])
                .text(ubic[0] + " - " + ubic[1]);
            if (ubic[0] == queryDict.ubic) {
                elem.attr("selected", "selected");
            }
            select.append(elem);
        });
    }
}

function cambiar_ubicacion(event) {
    var new_value = $(event.currentTarget).val();
    var opciones = $(".opciones");
    location.href = "?ubic=" + new_value;
}

function verificar_overflow() {
    var candidatos = document.querySelectorAll(".candidato");
    for (var i = 0; i < candidatos.length; i++) {
        if (candidatos[i].scrollHeight > candidatos[i].clientHeight)
            candidatos[i].style.background = "red";
        if (candidatos[i].scrollWidth > candidatos[i].clientWidth)
            candidatos[i].style.background = "red";
    }
}

function select_grilla_is_open() {
    const select = document.querySelector("#template_selector select");
    return $(select).is(":focus");
}

const select_template_valor_inicial = () => {
    const clases = Array.from(
        document.querySelector(`.${contenedor_items_grilla_classname()}`)
            .classList
    );
    const clase_prefix = clases.find((clase) =>
        clase.startsWith(clase_grilla_prefix())
    );
    if (!clase_prefix) return;
    const select_value = clase_prefix.split(clase_grilla_prefix())[1];
    document.querySelector("#template_selector select").value = select_value;
};

function contenedor_items_grilla_classname() {
    return en_confirmacion() ? "confirmados" : "opciones";
}

function clase_grilla_prefix() {
    return en_confirmacion() ? "confirmacion" : "max";
}

function en_confirmacion() {
    return (
        document.getElementById("pantalla_confirmacion").offsetParent !== null
    );
}

function _seleccion_mock() {
    const seleccion_random = {};
    codigos_cargos().forEach((c) => {
        const candidato = random_candidatura(c);
        seleccion_random[c] = [`${candidato.id_umv}`];
        if (tiene_preferentes_seleccionables(candidato)) {
            if (!("preferencias" in seleccion_random))
                seleccion_random.preferencias = {};
            seleccion_random.preferencias = {
                ...seleccion_random.preferencias,
                ...{
                    [c]: [random_preferente(candidato)],
                },
            };
        }
    });
    return seleccion_random;

    function tiene_preferentes_seleccionables(candidato) {
        return (
            !candidatura_es_especial(candidato) &&
            es_candidato_con_preferentes(candidato)
        );
    }
    function codigos_cargos() {
        return local_data.categorias._data.map((c) => c.codigo);
    }
    function random_candidatura(codigo_cargo) {
        return random_item(
            local_data.candidaturas._data.filter(
                (i) =>
                    i.cod_categoria === codigo_cargo && i.clase !== "Especial"
            )
        );
    }
    function random_preferente(candidato) {
        const preferentes = [
            ...candidato.secundarios_datos_extra.map((p) => p.id_candidatura),
            candidato.codigo,
        ];
        return random_item(preferentes);
    }
    function random_item(array) {
        return array[Math.floor(Math.random() * array.length)];
    }
}
