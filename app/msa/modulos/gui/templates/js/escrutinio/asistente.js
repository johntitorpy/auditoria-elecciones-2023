/**
 * @namespace js.escrutinio.asistente
 */

/* Contiene el manejo de los slides del asistente. */
var _slide_index = null;

/**
 * Muestra la pantalla del asistente de cierre.
 * 
 * @param {*} datos_qr - Datos provenientes del qr.
 */
function pantalla_asistente_cierre(datos_qr){
    if(datos_qr == null){
      document.querySelector('.con-qr').style.display = 'none';
      document.querySelector('#slide_certificados_extra.slide .contenido-slide').style.top = "35%";
    } else {
        const svg_data = decodeURIComponent(datos_qr);
        Array.from(
            document.querySelectorAll('.imagen_qr')
        ).map( 
            (i) => {
                i.src = svg_data;
            }
        )
    }
    get_next_slide();

    document.querySelector('#panel_asistente #boton_anterior').addEventListener('click', get_prev_slide );
    document.querySelector('#panel_asistente #boton_siguiente').addEventListener('click', get_next_slide );
    document.querySelector('#panel_finalizar #boton_finalizar').addEventListener('click', mensaje_confirmacion_apagar );
}

/** Muestra un slide en particular del asistente. */
function show_slide(){
    var slide = slides_asistente[_slide_index];
    if(typeof(slide) != "undefined"){
        if(_slide_index == slides_asistente.length - 1){
            document.querySelector('#panel_asistente #boton_siguiente').style.display = 'none';
            document.querySelector('#panel_finalizar #boton_finalizar').style.display = 'block';
            document.querySelector('#panel_asistente #boton_anterior').classList.add('borderless');
        } else {
            document.querySelector('#panel_asistente #boton_siguiente').style.display = 'block';
            document.querySelector('#panel_finalizar #boton_finalizar').style.display = 'none';
            document.querySelector('#panel_asistente #boton_anterior').classList.remove('borderless');
        }

        if(_slide_index === 0){
            document.querySelector('#panel_asistente #boton_anterior').style.display = 'none';
        } else {
            document.querySelector("#panel_asistente #boton_anterior").style.display = 'block';
        } 
        patio[slide.id].only();
    }
}

/** Muestra el proximo slide. */
function get_next_slide(){
    sonido_tecla();
    if(_slide_index === null){
        _slide_index = 0;
    } else {
        _slide_index += 1;
    }
    show_slide();
}

/** Muestra el anterior slide. */
function get_prev_slide(){
    sonido_tecla();
    _slide_index -= 1;
    show_slide();
}

/** Le avisa al backend para salir del modulo. */
function salir(){
    sonido_tecla();
    send("salir");
}

/** Le avisa al backend para apagar la maquina. */
function apagar(){
    sonido_tecla();
    send("apagar");
}
