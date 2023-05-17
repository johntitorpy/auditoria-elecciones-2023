/**
 * @namespace js.menu.funciones
 */
let patio = null;
var ultimo_estado = null;
var seleccion_actual = null;
var puede_cambiar_vista = false;
/**
 * Se dispara cuando se terminó de cargar la pagina.
 */
function document_ready(){
    preparar_eventos();
    document.addEventListener("dragstart", (event) => { event.target.click(); });
    load_ready_msg();

    /**@todo: revisar por qué se agregó esta linea de codigo. */
    const popup_btn = document.querySelector(".popup .btn")
    if (popup_btn) popup_btn.addEventListener("click", click_boton_popup);
};

ready(document_ready);

/**
 * Crea el objeto Patio si no fue ya creado.
 * @returns {Promise} 
*/
function load_patio(){
    if (patio !== null) {
        return Promise.resolve();
    }
    patio = new Patio(
        document.querySelector("#pantallas"), 
        pantallas, 
        contexto,
        "pantallas/menu"
    );
    return patio.load();                   
}

/**
* Carga lockscreen.
*/
function mostrar_lockscreen() {
    hide_dialogo();
    patio.lockscreen.only();
}

/**
* Carga botonera.
*/
const mostrar_botonera = () => {
    patio.botonera.only();
}

/**
 * Muestra pantalla de menú segun los estados de las variables 
 * "USAR_ASISTIDA", "USAR_VOTO", "USAR_TOTALIZADOR" y "USAR_CAPACITACION".
 * 
 * @param {*} data - Objeto que contiene las variables "USAR_ASISTIDA", "USAR_VOTO", "USAR_TOTALIZADOR" y "USAR_CAPACITACION".
 */
function mostrar_pantalla(data){
    mostrar_botonera();
    if(data.USAR_ASISTIDA){
        document.querySelector('#btn_asistida').style.display = 'block';
        document.querySelector("#btn_asistida ~ .boton-central").classList.add('con-tercio');
    }

    if(!data.USAR_VOTO){
        document.querySelector('btn_sufragio').style.display = 'none';
    }

    if(data.USAR_TOTALIZADOR){
        document.querySelector('#btn_totalizador').style.display = 'block';
        document.querySelector('#btn_totalizador ~ .boton-central').classList.add('con-tercio');

    }

    if(data.USAR_COPIAS_CERTIFICADO){
        //$("#btn_copias_certificado").show();
	    document.querySelector("#btn_copias_certificado").style.display = 'block';
        //$("#btn_copias_certificado ~ .boton-central").addClass("con-tercio");
	    document.querySelector("#btn_copias_certificado").previousElementSibling.classList.add('con-tercio');
    }

    if(data.USAR_CAPACITACION){
        document.querySelector('#btn_capacitacion').style.display = 'block';
    }

}

/**
 * Maneja el clic en el botón según la clase de dicho botón.
 * Las opciones son apagar la máquina, calibrarla, 
 * salir al módulo de escrutinio o salir al módulo de sufragio.
 * 
 * @param {*} target - Elemento html cliqueado.
 */
function click_boton(target){
    var parts = target.id.split("btn_");
    target = document.querySelector('#' + target.getAttribute('id'));
    target.classList.add("seleccionado");
    var modulo = parts[1];
    if(modulo == "apagar"){
        apagar();
    } else if(modulo == "calibrar"){
        calibrar();
    } else {
        if(modulo == "escrutinio"){
            if(constants.CON_DATOS_PERSONALES){
                modulo = "ingreso_datos,escrutinio";
            }
        } else if(modulo == "sufragio") {
            var icono = document.querySelector("#icono_sufragio");    
            var svg = icono.contentDocument;
            var paths = svg.querySelector("#paths");
            var color = target.style.borderTopColor;
            paths.style.fill = color
        }
        salir_a_modulo(modulo);
    }
}

/**
 * Llama a una función que muestra el boton de mantenimiento.
 */
function mostrar_boton_mantenimiento(){
    show_btn_mantenimiento();
}

/**
 * Genera el html del diálogo de confirmación del apagado de la máquina.
 * Esta función es llamada desde ```cargar_dialogo``` (ver popup.js). 
 */
function msg_confirmacion_apagar(){
    var boton_apagar = document.querySelector("#btn_apagar");
    boton_apagar.classList.remove("seleccionado");
    const generador_html = (template) => {
        var mensaje = constants.i18n.esta_seguro_apagar;
        var template_data = {
            pregunta: mensaje,
            btn_aceptar: true,
            btn_cancelar: true,
        };
        return template(template_data);
    }
    return promise_popup("popup", "partials/popup", generador_html);
}

/**
 * Devuelve el título del menú.
 * @returns {Object} Json que contiene la clave "titulo_menu" con el valor :const:`<constants.i18n.titulo_menu>`
 */
function popular_titulo(){
    return {
        "titulo_menu": constants.i18n.titulo_menu
    };
}

