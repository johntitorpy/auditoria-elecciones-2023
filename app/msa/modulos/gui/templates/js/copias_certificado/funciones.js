function document_ready(){
    preparar_eventos();
    bind_event_to_click("dragstart", document);
    load_ready_msg();
    asignar_evento(".popup-box", restaurar_foco_invalido, "hideDialogo");
    asignar_evento("#accesibilidad li", salir);    
}

ready(document_ready);

const bind_event_to_click = (tipo_evento, element) => {
    element.addEventListener(tipo_evento, (event) => {
        event.target.click();
    });
};

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
    const tiene_tooltip = destination && destination.dataset && destination.dataset.tooltip
    const ingreso = document.querySelector(".ingreso");
    const ingreso_tooltip = document.querySelector(".ingreso + .tooltip");
    if (tiene_tooltip) {
        ingreso.classList.add("con-tooltip");
        ingreso_tooltip.style.display = "block";
    } else {
        ingreso.classList.remove("con-tooltip");
        ingreso_tooltip.style.display = "none";
    }
}

function error_secuencia() {
    let elem_text_tooltip = document.getElementById('_txt_acerque_acta_cierre')
    elem_text_tooltip.innerText = 'Las actas fueron ingresadas en el orden incorrecto. Empiece nuevamente desde la' +
        ' primera.'


    document.querySelector('div.tooltip_wrapper').style.boxShadow = 'inset 0px 0px 9px 9px orange'
    setTimeout(function () {
        document.querySelector('div.tooltip_wrapper').style.boxShadow = 'none'
    },2500)
}

function secuencia_correcta(data) {
    let elem_text_tooltip = document.getElementById('_txt_acerque_acta_cierre')
    elem_text_tooltip.innerText = 'Acta cargada correctamente. Actas restantes: '+ data['partes']

    document.querySelector('div.tooltip_wrapper').style.boxShadow = 'inset 0px 0px 9px 9px green'
    setTimeout(function () {
        document.querySelector('div.tooltip_wrapper').style.boxShadow = 'none'
    },2500)
}


function set_mensaje(data) {
    document.querySelector(".contenedor-texto h1").innerHTML = data;
}

function salir() {
    send("salir");
}

function show_body(){
    /**/
}
