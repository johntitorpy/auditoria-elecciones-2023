/**
 * @namespace js.escrutinio.clasificacion
 */

/* Cosas relacionadas a la pantalla de clasificación de votos */

/**FIXME: Reducir el uso de variables globales. */
var _pantalla_clasificacion_cargada = false;
var _en_clasificacion = false;

/** Vuelve a la pantalla de recuento. */
function volver_al_recuento(){
    document.querySelector('#cantidad_escrutadas').style.display = "";
    send("habilitar_recuento");
    pantalla_inicial();
    _en_clasificacion = false;
}

/** Muestra como activo el campo anterior. */
function anterior_clasificacion(){
    sonido_tecla();
    var index = _campo_get_index();
    if(index){
        _campo_get(index - 1);
        actualizar_botones_panel();
    } else {
        volver_al_recuento();
    }
}

/** Muestra como activo el campo siguiente. */
function siguiente_clasificacion(){
    sonido_tecla();
    var index = _campo_get_index();
    _campo_get(index + 1);
    actualizar_botones_panel();
}

/** Actualiza los botones del panel segun el estado. */
function actualizar_botones_panel(){
    var index = _campo_get_index();
    var len_campos = _campo_get_ids().length;
    if(index == len_campos - 1){
        document.querySelector('#boton_siguiente').style.display = 'none';
        document.querySelector('#boton_imprimir').style.display = 'block';
        document.querySelector('#_txt_volver').innerHTML = constants.i18n.palabra_anterior;
    } else if (index === 0){
        document.querySelector('#boton_siguiente').style.display = 'block';
        document.querySelector('#boton_imprimir').style.display = 'none';
        document.querySelector('#_txt_volver').innerHTML = constants.i18n.volver;
    } else {
        document.querySelector('#boton_siguiente').style.display = 'block';
        document.querySelector('#boton_imprimir').style.display = 'none';
        document.querySelector('#_txt_volver').innerHTML = constants.i18n.palabra_anterior;
    }

    const elemento_seleccionado = document.querySelector(
        ".seleccionado[id]"
    )
    if (!elemento_seleccionado)
        return

    const cod_especial = elemento_seleccionado.getAttribute("id").split("_")[1];
    var contenido = constants.descripcion_especiales[cod_especial];        
    let contenido_votos_computar = contenido + '<div id="contenedor_img_votos_computar"><img src="img/imagen_votos_computar.png" alt="votos a computar"> </div>'
    var titulo = constants.titulos_especiales[cod_especial];
    document.querySelector("#definiciones > .titulo").innerHTML = titulo;
    if(cod_especial == 'VAC') {
        if (document.querySelector("#contenedor_img_votos_computar") === null){
            document.querySelector("#definiciones > .contenido").innerHTML = contenido_votos_computar;
        }
    }else{
        document.querySelector("#definiciones > .contenido").innerHTML = contenido;
    }
}

/** Genera la pantalla de clasificación de votos. */
function generar_clasificacion_de_votos(datos){
    listas = [];
    var obj_procesadas = {
        "id_campo": "boletas_procesadas",
        "cantidad": datos.boletas_procesadas,
        "titulo": constants.i18n.boletas_procesadas,
        "editable": false,   
    };
    listas.push(obj_procesadas);

    for(var i in datos.listas_especiales){
        var codigo = datos.listas_especiales[i];
        var obj_especial = {
            "id_campo": codigo,
            "cantidad": 0,
            "titulo": constants.titulos_especiales[codigo],
            "editable": true,
        };
        listas.push(obj_especial);
    }

    var obj_totales = {
        "id_campo": "boletas_totales",
        "cantidad": datos.boletas_totales,
        "titulo": constants.i18n.total_general,
        "editable": false,   
    };
    listas.push(obj_totales);
    return listas;    
}

const render_campos_extra = (contenedor, template_campo_extra, listas) => {
    contenedor.innerHTML = '';
    listas.map(
        (lista) => contenedor.insertAdjacentHTML(
            'beforeend', 
            template_campo_extra(lista)
        )
    );
} 

/** 
 * Carga las acciones que se ejecutan cuando se presiona en los botones de 
 * cambio del valor de la cantidad de votos de una lista especial.
*/
const actualizar_botones_campos_extras = () => {
    Array.from(document.querySelectorAll('.btn-subir')).map(
        btn => {
            btn.addEventListener('click', aumentar_valor_especial)
        }
    )
    Array.from(document.querySelectorAll('.btn-bajar')).map(
        btn => {
            btn.addEventListener('click', decrementar_valor_especial)
        }
    )
}

/**
 * Recibe una función ```cambiar_valor``` y devuelve otra función que ante un evento ejecuta dicha función.
 * 
 * @param {function} cambiar_valor - Acción que cambia el valor de la lista especial.
 * @returns {function} - Función que recibe un evento y realiza la acción de cambiar el valor de la lista especial.
 */
const cambiar_valor_lista_especial = cambiar_valor => event => {
    sonido_tecla();
    const element_id = event.currentTarget.dataset.target
    const elemento = document.getElementById(element_id);
    const numero = Number(elemento.textContent);
    cambiar_valor(elemento, numero)
    total_boletas()
}

/** Baja en uno el numero dado y se lo asigna al elemento recibido.*/
const bajar_numero = (elemento, numero) => {
    if (numero <= 0) return
    elemento.textContent = numero - 1;
    elemento.dataset.value = numero - 1
}

/** Sube en uno el numero dado y se lo asigna al elemento recibido.*/
function subir_numero(elemento, numero){
    elemento.textContent = numero + 1;
    elemento.dataset.value = numero + 1
}

/**Función que se asigna al botón de incrementar el número de votos de una lista especial. */
const aumentar_valor_especial = cambiar_valor_lista_especial(subir_numero)
/**Función que se asigna al botón de decrementar el número de votos de una lista especial. */
const decrementar_valor_especial = cambiar_valor_lista_especial(bajar_numero)


/**
 * Muestra la pantalla de clasificación de votos. 
 * Es llamada desde el backend a través del método "cargar_clasificacion_de_votos".
 * 
 * @param {*} datos - Contiene las listas especiales y las boletas procesadas entre otros datos.
 */
function pantalla_clasificacion_votos(datos){

    _en_clasificacion = true;

    //Saltea la clasificación si hay listas especiales.
    const saltear_clasificacion_votos =
        !_pantalla_clasificacion_cargada && !datos.listas_especiales.length;

    if (saltear_clasificacion_votos){
        iniciar_secuencia_impresion();
        return;
    }

    if(_pantalla_clasificacion_cargada){
        document.querySelector('#numero_boletas_procesadas').innerHTML = datos.boletas_procesadas;
        total_boletas();
        mostrar_pantalla_clasificacion();
        return;
    }
    
    if(datos.listas_especiales.length){

        const listas = generar_clasificacion_de_votos(datos);

        fetch_template("campo_extra", "pantallas/escrutinio").then(
            (campo_extra_template) => {
                const contenedor_campos_extra = document.querySelector('#campos_extra');
                if (contenedor_campos_extra) {
                    render_campos_extra(contenedor_campos_extra, campo_extra_template, listas);
                }
                asignar_evento('#panel_clasificacion #boton_volver', anterior_clasificacion);
                asignar_evento('#panel_clasificacion #boton_siguiente', siguiente_clasificacion);
                asignar_evento('#panel_clasificacion #boton_imprimir', mensaje_fin_escrutinio);
                asignar_evento('#campos_extra > .campo_editable', _campo_seleccionar);
                _pantalla_clasificacion_cargada = true;
                mostrar_pantalla_clasificacion();
            }
        );
    } 
}

const mostrar_pantalla_clasificacion = () => {
    const pantalla = patio.pantalla_clasificacion_votos;
    pantalla.only();
    _campo_get(0);
    actualizar_botones_panel();
    actualizar_botones_campos_extras()
}

/** 
 * Devuelve el índice del campo seleccionado. Si no hay un campo seleccionado devuelve -1.
 * 
 * @returns {Number} - Índice del campo actual.
*/
function _campo_get_index(){
    const campo_seleccionado = document.querySelector(
        ".seleccionado.campo_editable"
    )
    if (!campo_seleccionado) return -1

    const index = campo_seleccionado.getAttribute("id") 
    const campos = _campo_get_ids();
    return campos.indexOf(index);
}

/** 
 * Devuelve los ids de los campos editables.
 * 
 * @returns {String[]} - Ids de los campos editables. Ejemplo: [ "campo_NUL", "campo_TEC" ]
*/
const _campo_get_ids = () => Array.from(
    document.querySelectorAll(".campo_editable[id]")
).map(
    i => i.getAttribute("id")
)

/**
 * Marca al elemento de índice ``index`` como seleccionado.
 * 
 * @param {Number} index - Índice del campo.
 */
function _campo_get(index){
    Array.from(
        document.querySelectorAll('#campos_extra > .campo')
    ).map(
        elemento => elemento.classList.remove('seleccionado')
    )
    const campos_editables = Array.from(
        document.querySelectorAll(".campo_editable")
    )
    if (index >= 0 && index < campos_editables.length)
        campos_editables[index].classList.add("seleccionado")
}

/** Selecciona un campo. */
const _campo_seleccionar = (event) => {
    sonido_tecla();
    Array.from(
        document.querySelectorAll('#campos_extra > .campo')
    ).map(
        i => i.classList.remove('seleccionado')
    )
    event.currentTarget.classList.add("seleccionado");
    actualizar_botones_panel();
}

/** 
 * Llamada que se hace desde la pantalla de recuento para avisarle
 * al backend que se finalizó el recuento de los votos de la mesa. 
 * Ver función finalizar_recuento_boletas de recuento.js.
 */
function cargar_clasificacion_de_votos(){
    document.querySelector('#cantidad_escrutadas').style.display = 'none';
    send("cargar_clasificacion_de_votos");
}

/** 
 * Envía las listas especiales al backend. 
*/
function guardar_listas_especiales(){
    const elementos = Array.from(
        document.querySelectorAll(".valor.editable")
    )
    const listas = cargar_listas_especiales(elementos)
    send("guardar_listas_especiales", listas);
}

/** 
 * Devuelve los votos de las listas especiale. 
 * Los datos son tomados de los inputs de la pantalla.
 *
 * @returns {Object} - Listas especiales. Ejemplo: { "NUL": 10, "TEC": 0 }
 */
const cargar_listas_especiales = (elementos) => {
    return elementos.reduce(
        (prevItem, currentItem) => {
            const lista_especial_id = currentItem.id.split("_")[1]
            const lista_especial_value = Number(currentItem.textContent)
            prevItem[lista_especial_id] = lista_especial_value
            return prevItem
        },
        {}
    );
}

/** Calcula y muestra el número de boletas procesadas. */
const total_boletas = () => {
    const elemento_boletas_totales = document.querySelector('#valor_boletas_totales');
    elemento_boletas_totales.textContent = calcular_total_boletas();
}

const calcular_total_boletas = () => {
    const campos_editables_del_dom = Array.from(
        document.querySelectorAll(".valor.editable")
    )
    const elemento_numero_boletas_procesadas = document.getElementById(
        'numero_boletas_procesadas'
    )
    const tomar_text_content = dom_element => dom_element.textContent
    const convertir_a_entero = i => Number(i)
    const sumar_items = (prevItem, currentItem) => prevItem + currentItem

    return campos_editables_del_dom.concat(
        elemento_numero_boletas_procesadas
    ).map(
        tomar_text_content
    ).map(
        convertir_a_entero
    ).reduce(
        sumar_items
    )
}
