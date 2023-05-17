/**
 * @namespace js.sufragio.asistida
 */
/** Muestra el teclado "telefonico" de asistida. */
function mostrar_teclado(datos){
    const keyboard = document.querySelector('#keyboard-asistida');
    if (keyboard.innerHTML.trim() === ""){
        load_teclados(
            document.querySelector("#keyboard"), 
            document.querySelectorAll("#hidden_input"),    
            {
                layout: ["asistida"]
            }
        ).then(() => {
            patio_teclado.asistida.only();
        })   
    }
    patio.asistida_container.only();
}

/** Oculta el teclado. */
function ocultar_teclado(){
    patio.asistida_container.hide();
}

/** Callback de apretar el asterisco. */
function apretar_asterisco(){
    var input = document.querySelector("#hidden_input");
    asterisco(input.value);
    input.value = "";
}

/** Callback de apretar el numeral. */
function apretar_numeral(){
    var input = document.querySelector("#hidden_input");
    numeral(input.value);
    input.value = "";
}

/**
 *  Cambia el texto que mostramos como indicador de etapa para el acompañante vidente.
*/
function cambiar_indicador_asistida(data){
    document.querySelector("#indicador_asistida").innerHTML = data;
}

/**
 *  Emite el sonido de apretar cada tecla. 
 */
function beep(data){
    var tecla = data.innerHTML;
    if(tecla == "⁎"){
        tecla = "s";
    } else if(tecla == "#"){
        tecla = "p";
    }
    send("emitir_tono", tecla);
}

/** 
 * Establece la pantalla de seleccion de modos para asistida. 
 */
function pantalla_modos_asistida(){
    send("audios_pantalla_modos");
}

/** 
 * Carga los candidatos para asistida. Envía el mensaje ``audios_cargar_candidatos``.
 * 
 * @param {Object} data_dict - Diccionario que contiene entre otros datos los candidatos y las categorias.
 */
function cargar_candidatos_asistida(data_dict){
    var cods_candidatos = [];
    for(var i in data_dict.candidatos){
        cods_candidatos.push(data_dict.candidatos[i].id_umv);
    }

    if (typeof(data_dict.categoria.max_preferencias) !== "undefined"){
        if (typeof(_seleccion[data_dict.categoria.codigo]) === "undefined") {
            send("audios_cargar_listas_candidatos", [data_dict.categoria.codigo,
                 cods_candidatos]);
        }
    } else {
        send("audios_cargar_candidatos", [data_dict.categoria.codigo,
            cods_candidatos]);
    }
}

function seleccionar_preferente_asistida(params) {
    let cod_categoria = params[0];
    let codigos = params[1];

    categoria = local_data.categorias.one({codigo: cod_categoria});
    preferencias_tmp = codigos;
    //le paso uno de los seleccionados como candidato principal
    seleccionar_candidatos(categoria, [codigos[0]]);
}

/** 
 * Selecciona los candidatos. 
 * 
 * @param {Array} params - Lista de parámetros.
 */
function seleccionar_candidatos_asistida(params){
    categoria = local_data.categorias.one({codigo:params[0]});
    seleccionar_candidatos(categoria, params[1]);
}

/** 
 * Selecciona un partido. 
 * 
 * @param {Array} params - Lista de parámetros.
 */
function seleccionar_partido_asistida(params){
    categoria = local_data.categorias.one({codigo:params[1]});
    seleccionar_partido(params[0], categoria);
}

/**
 *  Muestra la confirmacion para asistida. Envía el mensaje ``audios_mostrar_confirmacion``.
 * 
 * @param {Array} paneles - Lista de paneles.
 */
function mostrar_confirmacion_asistida(paneles){
    datos = [];
    for(var i in paneles){
        var panel = paneles[i];
        if(panel.categoria.max_preferencias>0)
            var dato = [panel.categoria.codigo, panel.preferencias.map(i => i.id_umv)];
        else
            var dato = [panel.categoria.codigo, panel.candidato.id_umv];
        datos.push(dato);
    }
    confirmada = false;
    send("audios_mostrar_confirmacion", datos);
}

/**
* Carga las listas para Asistida. Si se agrupa por cargo se envía el mensaje ``audios_cargo_listas``, caso contrario, envía el mensaje ``audios_cargar_listas``.
* @param {Object} data 
* @param {boolean} agrupa_por_cargo 
* @param {boolean} hay_agrupaciones_municipales
*/
function cargar_listas_asistida(data, agrupa_por_cargo, hay_agrupaciones_municipales){
    if(typeof(candidatos) === "undefined"){
        candidatos = false;
    }
    var cods_listas = [];
    if(agrupa_por_cargo){
        for(var i in data){
            cods_listas.push(data[i].id_umv);
        }
        if (hay_agrupaciones_municipales) {
            cods_listas.push(0);
        }
        send("audios_cargo_listas", cods_listas);
    } else {
        for(var i in data){
            cods_listas.push(data[i].codigo);
        }
        if (hay_agrupaciones_municipales) {
            cods_listas.push(0);
        }
        send("audios_cargar_listas", cods_listas);
    }
}

/**
 * Carga los partidos para la categoria. Envía al backend el mensaje ``audios_partidos_categoria``.
 * @param {Object} data_dict - Json que contiene los partidos y categorias
 */
function cargar_partidos_categoria_asistida(data_dict){
    var cods_listas = [];
    partidos = data_dict['partidos'];
    let filter_alianza_candidato = {
        "cod_categoria": data_dict.categoria.codigo,
        "clase": "Candidato"
    };
    for(var i in partidos){
        filter_alianza_candidato["cod_alianza"] = partidos[i].codigo;
        let partido_con_candidatos = local_data.candidaturas.one(filter_alianza_candidato) !== undefined;
        if (partido_con_candidatos)
            cods_listas.push(partidos[i].id_candidatura);
    }
    send("audios_partidos_categoria",
         [data_dict.categoria.codigo, cods_listas]);
}

/**
 * Carga los partidos en lista completa para asistida. Envía al backend el mensaje ``audios_partidos_completa``.
 * @param {Object} data_dict - Json que contiene los partidos.
 */
function cargar_partidos_completa_asistida(data_dict){
    var cods_listas = [];
    partidos = data_dict['partidos'];
    for(var i in partidos){
        cods_listas.push(partidos[i].id_candidatura);
    }
    send("audios_partidos_completa", cods_listas);
}

/**
 * Carga consulta popular de asistida. Envía al backend el mensaje ``audios_cargar_consulta``.
 * @param {Object} data_dict - Json que contiene los candidatos.
 */
function cargar_consulta_popular_asistida(data_dict){
    var cods_candidatos = [];
    for(var i in data_dict.candidatos){
        cods_candidatos.push(data_dict.candidatos[i].id_umv);
    }
    send("audios_cargar_consulta",
         [data_dict.categoria.codigo, cods_candidatos]);
}

function cargar_preferencias_candidato_asistida(data_dict){
    /* Carga consulta popular de asistida exceptuando los que ya fueron seleccionados. */
    send("audios_cargar_preferencias_candidato", [data_dict.id_umv]);
}
