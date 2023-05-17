/**
 * @namespace js.escrutinio.mensajes
 */

/**
 * Se crea una variable global para poder volver a la pantalla anterior
 * luego de hacer clic en cancelar en las pantallas con mensaje de salida.
 * Sin esta variable global no se podía acceder a esta información.
 * Posiblemente se necesite un refactor para mejorar esta funcionalidad 
 * y no depender de esta variable.
 */
let data_cancelar = {}


/**
 * Genera la estructura que contiene los datos correspondientes 
 * a cada uno de los mensajes que se pueden llegar a mostrar en 
 * la pantalla de escrutinio.
 */
const generar_mensajes_data = () => {
    return [
        {
            nombre: "pocas_boletas",
            pantalla_patio: "mensaje_pocas_boletas",
            accion_aceptar: accion_en_boton_factory(pocas_boletas_aceptar),
            accion_cancelar: accion_en_boton_factory(pocas_boletas_cancelar)
        },
        {
            nombre: "salir",
            pantalla_patio: "mensaje_salir",
            accion_aceptar: accion_en_boton_factory(salida_aceptar),
            accion_cancelar: accion_en_boton_factory(salida_cancelar)
        },
        {
            nombre: "fin_escrutinio",
            pantalla_patio: "mensaje_fin_escrutinio",
            accion_aceptar: accion_en_boton_factory(fin_escrutinio_aceptar),
            accion_cancelar: accion_en_boton_factory(fin_escrutinio_cancelar)
        },
        {
            nombre: "confirmar_apagar",
            pantalla_patio: "mensaje_confirmar_apagar",
            accion_aceptar: accion_en_boton_factory(confirmacion_apagar_aceptar),
            accion_cancelar: accion_en_boton_factory(confirmacion_apagar_cancelar)
        }
    ]
}


/** Mensaje de pocas boletas escrutadas. */
const mensaje_pocas_boletas = () => {
    const mensaje_nombre = "pocas_boletas";
    pantalla_mensaje(mensaje_nombre)
}

/** Acción cuando el usuario da al boton aceptar del mensaje de pocas boletas. */
const pocas_boletas_aceptar = () => {
  cargar_clasificacion_de_votos();
}

/** Acción cuando el usuario da al boton cancelar del mensaje de pocas boletas. */
const pocas_boletas_cancelar = () => {
    pantalla_inicial(); 
}


/** Mensaje de salida. Para pedir al usuario que confirme si desea salir.*/
var preguntar_salida = () => {
    if (patio.last_shown !== "mensaje_salir"){
        borrar_resaltado();
        const mensaje_nombre = "salir"
        pantalla_mensaje(mensaje_nombre)
        hide_dialogo();
        const last_tile = patio.last_shown;
        if (last_tile == "pantalla_copias"){
            document.querySelector(pantalla.id + " .texto-secundario").style.display = 'none';
        }
    }
}

/** Acción cuando el usuario da al boton aceptar del mensaje de salida. */
const salida_aceptar = () => {
    send("aceptar_salida");
}

/**
 * Determina a qué pantalla se vuelve cuando se apoya una credencial.
 * Como se cancela la acción de salir, es necesario volver a la última 
 * pantalla que se vio.
 */
const cancelar_con_credencial = () => {

    patio[data_cancelar.pantalla_anterior].only()
    
}

/**
 * Acción cuando el usuario da al boton cancelar del mensaje de salida.
 * Tomar especial atención al flujo de cancelar la salida, ya que hay que volver al contexto correcto.
 */
const salida_cancelar = () => {
    const last_tile = data_cancelar.pantalla_anterior;
    if(last_tile == "mensaje_pocas_boletas" ||
       last_tile == "pantalla_boleta" ||
       last_tile == "pantalla_boleta_repetida" ||
       last_tile == "pantalla_boleta_error"
       ){
        pantalla_inicial(); 
    }
    else if(last_tile == "mensaje_fin_escrutinio"){
        // No hago nada en especial, mas que pasar de largo, quiero que
        // tire el "cancelar" del popup del fin de escrutinio pero que no
        // tire muestre el popup de cancelar que va a mostrar por 200
        // milisegundos y queda raro. Lo dejo explicito aca para futura
        // referencia.
        cargar_clasificacion_de_votos();
    }
    else {
        patio[last_tile].only();
    }
}


/**
* Este es el mensaje de fin de escritinio, si acepta no hay vuelta
* atrás y solo se pueden imprimir actas. El usuario tiene que estar 100%
* seguro de que no quiere sumar ningun voto más ni agregar ningun voto a
* las "listas especiales" (clasificaciones de votos).
*/
const mensaje_fin_escrutinio = () => {
    const mensaje_nombre = "fin_escrutinio";
    pantalla_mensaje(mensaje_nombre);
    sonido_tecla();
}

/** Acción cuando el usuario da al botón aceptar del mensaje de fin de escrutinio. */
const fin_escrutinio_aceptar = () => {
    guardar_listas_especiales();
    iniciar_secuencia_impresion();
}

/** Acción cuando el usuario da al botón cancelar del mensaje de fin de escrutinio. */
const fin_escrutinio_cancelar = () => {
    if (constants.totalizador) {
        // Volver al inicio para poder seguir totalizando recuentos:
        pantalla_inicial();
    } else {
        //Aca llamamos de nuevo a la pantalla de carga pero via el backend,
        //para explicitamente volver a armarla.
        cargar_clasificacion_de_votos();
    }
}


/** 
 * Pide confirmación del apagado de la máquina.
 */ 
const mensaje_confirmacion_apagar = () => {
    const mensaje_nombre = "confirmar_apagar"
    pantalla_mensaje(mensaje_nombre);
}
/** Acción cuando el usuario da al botón aceptar del mensaje de confirmar apagar la máquina. */
const confirmacion_apagar_aceptar = () => {
    apagar();
}

/** Acción cuando el usuario da al botón cancelar del mensaje de fin de escrutinio. */
const confirmacion_apagar_cancelar = () => {
    show_slide();
}


/********************************************************  
 * 
 * HELPERS
 * 
********************************************************/

 /**
 * Devuelve una función que es la que se asignará al botón de aceptar o cancelar.
 * Inyecta a la ```acción``` dada las llamadas que son comunes a todos los eventos de los botones. 
 * Por ejemplo, siempre que se presiona un botón del mensaje se desea que la máquina 
 * haga un sonido de tecla, sea cual sea la acción particular del botón. 
 * Ejemplo de llamada: const on_aceptar_salida = accion_en_boton_factory(aceptar_salida)
 * Luego, on_aceptar_salida ya puede ser asignado a un evento usando addEventListener, por ejemplo.
 * 
 * @param {function} accion - Función que se ejecuta cuando se hace clic en el botón. 
 * @param {function} [pre_accion=sonido_tecla] - Función que se ejecuta antes de la acción. Por default se llama a sonido_tecla()
 * @param {function} [post_accion=desbindear_panel_acciones] - Función que se ejecuta después de la acción. Por default se llama a desbindear_panel_acciones()
 * @returns {function} - Función que se asignará al botón de aceptar o cancelar.
 */
const accion_en_boton_factory = (
    accion, 
    pre_accion = sonido_tecla,
    post_accion = desbindear_panel_acciones
) => () => {
    pre_accion();
    accion();
    post_accion();
}

const pantalla_mensaje = (nombre_mensaje) => {
    const mensaje = mensajes_data.find( 
        (mensaje) => mensaje.nombre == nombre_mensaje
    );
    if (!mensaje) return;
    inicializar_botones(mensaje)
    mostrar_mensaje_en_pantalla(mensaje)
}

const inicializar_botones = (mensaje) => {
    data_cancelar = {pantalla_anterior: patio.last_shown}
    bindear_panel_acciones(
        mensaje.accion_aceptar,
        mensaje.accion_cancelar
    )
}

const mostrar_mensaje_en_pantalla = (mensaje) => {    
    patio[mensaje.pantalla_patio].only()
}

/**
 * Función para asignar acciones a los botones de aceptar y cancelar de los
 * mensajes que muestra la pantalla de escrutinio. Antes de dicha asignacion 
 * se llama a la funcion "accion_previa" la cual por default borra los eventos 
 * ya asignados a los botones. Esto se hace para asegurar que los botones solo 
 * tienen una accion asignada por evento.
 * @param {function} accion_aceptar - Función que se asigna al botón de aceptar.
 * @param {function} accion_cancelar - Función que se asigna al botón de cancelar.
 * @param {function} [accion_previa=desbindear_panel_acciones] - Función ejecutada antes de bindear los botones.
 * @param {string} [tipo_evento="click"] - Tipo de evento a escuchar.
 * @param {object} [btn_aceptar=document.getElementById("boton_aceptar")] - Elemento al cual se le asigna la acción de aceptar.
 * @param {object} [btn_cancelar=document.getElementById("boton_cancelar")] - Elemento al cual se le asigna la acción de cancelar.
 */
const bindear_panel_acciones = (
    accion_aceptar,
    accion_cancelar, 
    accion_previa = desbindear_panel_acciones, 
    tipo_evento = "click",
    btn_aceptar = document.getElementById("boton_aceptar"),
    btn_cancelar = document.getElementById("boton_cancelar")
) => {
    accion_previa()
    btn_aceptar.addEventListener(tipo_evento, accion_aceptar);
    btn_cancelar.addEventListener(tipo_evento, accion_cancelar);
}

/**
 * Quita o desbindea el comportamiento del panel de acciones.
 */
const desbindear_panel_acciones = (
    btn_aceptar = document.getElementById("boton_aceptar"),
    btn_cancelar = document.getElementById("boton_cancelar")
) => {
    const eliminar_evento = (
        btn, accion, tipo_accion="click"
    ) => btn.removeEventListener(tipo_accion, accion)

    mensajes_data.map( 
        (m) => {
            eliminar_evento(btn_aceptar, m.accion_aceptar)  
            eliminar_evento(btn_cancelar, m.accion_cancelar) 
        }
    )
}

/********************************************************  
 * 
 * FIN de HELPERS
 * 
********************************************************/

 /**
  * Estructura de datos que tiene datos de cada mensaje.
  * Se genera al final de este archivo y no deben ser mutados.
 **/
const mensajes_data = generar_mensajes_data();