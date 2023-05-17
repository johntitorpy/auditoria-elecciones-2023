function pantalla_prueba_equipo() {


    console.log('INGRESO A CARGAR_TEMPLATES');

    const promise_ingreso_boleta = fetch_template(
        "ingreso_boleta",
        "pantallas/prueba_equipo"
    );
    
    const promise_grabado_impresion_boleta = fetch_template(
        "grabado_impresion_boleta",
        "pantallas/prueba_equipo"
    );
    
    const promise_verificacion_boleta = fetch_template(
        "verificacion_boleta",
        "pantallas/prueba_equipo"
    );
    
    const promise_validacion_chip = fetch_template(
        "validacion_chip",
        "pantallas/prueba_equipo"
    );
    
    const promise_leyenda_verificacion_chip = fetch_template(
        "leyenda_verificacion_chip",
        "pantallas/prueba_equipo"
    );
    
    const promise_mensaje_finalizacion = fetch_template(
        "mensaje_finalizacion",
        "pantallas/prueba_equipo"
    );
    
    const promise_pop_up_verificar_chip = fetch_template(
        "pop_up_verificar_chip",
        "pantallas/prueba_equipo"
    );
    
    
    
    
    Promise.all([promise_ingreso_boleta, promise_grabado_impresion_boleta, promise_verificacion_boleta,
        promise_validacion_chip, promise_leyenda_verificacion_chip, promise_mensaje_finalizacion, 
        promise_pop_up_verificar_chip])
        .then(
        ([template_ingreso_boleta, template_grabado_impresion_boleta, template_verificacion_boleta,
            template_validacion_chip, template_leyenda_verificacion_chip, template_mensaje_finalizacion, 
            template_pop_up_verificar_chip]) => {
            const template_data = {
                mensaje: "",
            };
            const html_pantallas_ingreso_boleta = template_ingreso_boleta(template_data);
            const html_pantallas_grabado_impresion_boleta = template_grabado_impresion_boleta();
            const html_pantallas_verificacion_boleta = template_verificacion_boleta();
            const html_pantallas_validacion_chip = template_validacion_chip();
            const html_pantallas_leyenda_verificacion_chip = template_leyenda_verificacion_chip();
            const html_pantallas_mensaje_finalizacion = template_mensaje_finalizacion();
            const html_pantallas_pop_up_verificar_chip = template_pop_up_verificar_chip();
            console.log('ANTES de agregar el template');
            console.log(document.querySelector("#contenedor_pantallas"));
        
            document.querySelector(
                "#contenedor_pantallas"
            ).innerHTML = html_pantallas_ingreso_boleta + 
                        html_pantallas_grabado_impresion_boleta + 
                        html_pantallas_verificacion_boleta +
                        html_pantallas_validacion_chip + 
                        html_pantallas_leyenda_verificacion_chip + 
                        html_pantallas_mensaje_finalizacion +
                        html_pantallas_pop_up_verificar_chip;
        
            console.log('DESPUES de agregar el template');
            console.log(document.querySelector("#contenedor_pantallas"));

            pantalla_ingreso_boleta()
        }
    )
}

function pantalla_ingreso_boleta(data){

    // hide_elements('.generacion_boletas_prueba')
    hide_elements('.cdqc_pantalla_grabado_impresion')
    hide_elements('.cdqc_pantalla_verificacion_boleta')
    hide_elements('.cdqc_pantalla_validacion_rfid')
    hide_elements('.cdqc_pantalla_leyenda_verificacion_chip')
    hide_elements('.cdqc_pantalla_finalizacion_verificacion')
    hide_elements('.popup')
    hide_elements(".btn_continuar");


    // document.querySelector("#logo_eleccion")?.style.display = "none";
    document.querySelector("#_txt_encabezado").innerText =
    constants.i18n.encabezado_prueba_maquina;

    document.getElementsByClassName("generacion_boletas_prueba-texto")[0].innerText =
        "A. " + constants.i18n.generacion_boleta_prueba_maquina;

    document.getElementsByClassName("generacion_boletas_prueba-texto_secundario")[0]
        .innerText = constants.i18n.inserte_boleta_impresora
        


    const img = document.getElementsByClassName("generacion_boletas_prueba-img")[0];

    if (window.matchMedia("(min-width: 1920px)").matches) {
        img.src = "img/prueba_equipo/p6_insertar.png";
    }
    else{
        img.src = "img/prueba_equipo/p4_insertar.png";
    }

    
}




function pantalla_paso_2(data){


    hide_elements('.generacion_boletas_prueba');
    show_elements('.cdqc_pantalla_grabado_impresion');
    hide_elements('.cdqc_pantalla_verificacion_boleta');
    hide_elements('.cdqc_pantalla_validacion_rfid');
    hide_elements('.cdqc_pantalla_leyenda_verificacion_chip');
    hide_elements('.cdqc_pantalla_finalizacion_verificacion');
    hide_elements('.popup');
    hide_elements('.btn_repetir');
    hide_elements('.btn_continuar_pantalla');
    hide_elements('.btn_reiniciar')


    const text = document.querySelector(".cdqc_pantalla_grabado_impresion")
    const titulo_pantalla_2 = text.children[0];
    console.log(titulo_pantalla_2);
    titulo_pantalla_2.innerHTML =
    "A. " + constants.i18n.generacion_boleta_prueba_maquina;
    
    circle_primario = document.getElementsByClassName("generacion_boletas_prueba-circle_primario")[0];
    numero_primario = document.getElementsByClassName("generacion_boletas_prueba-numero_primario")[0];
    circle_secundario = document.getElementsByClassName("generacion_boletas_prueba-circle_secundario")[0];
    numero_secundario = document.getElementsByClassName("generacion_boletas_prueba-numero_secundario")[0];
    grabar_chip = document.getElementsByClassName("generacion_boletas_prueba-grabar_chip")[0];
    imprimir = document.getElementsByClassName("generacion_boletas_prueba-imprimir_boleta")[0];

    document.getElementsByClassName("check-imprimir")[0].style.display = "none";
    document.getElementsByClassName("alert-chip")[0].style.display = "none";
    document.getElementsByClassName("alert-imprimir")[0].style.display = "none";
    document.getElementsByClassName("generacion_boletas_prueba-texto_secundario")[0].style.display = "none";
    numero_primario.innerText = "1";
    grabar_chip.innerText = constants.i18n.grabar_chip
    numero_secundario.innerText = "2";
    imprimir.innerText = constants.i18n.palabra_imprimir


    if (!data.error){
        hide_elements('.check-chip')
        hide_elements('.btn_repetir');
        hide_elements('.btn_continuar_pantalla');
        show_elements('.alert-chip')
        show_elements('.btn_reiniciar')
        grabar_chip.style.color = 'red';
        circle_primario.style.background = 'red';
        const btn = document.querySelector('.btn_reiniciar')
        btn.innerText = constants.i18n.btn_reintentar
        document.getElementsByClassName("generacion_boletas_prueba-texto_chip")[0].innerText = data.mensaje;
        change_botton_enable()
        document.querySelectorAll(".btn_reiniciar").forEach((btn) => {
            btn.addEventListener("click", () => send("reinicio_pantallas"));
        });

    }
    else{
        document.getElementsByClassName("check-chip")[0].style.display = "none";
        textoChip = document.getElementsByClassName("generacion_boletas_prueba-texto_chip")[0];
        document.getElementsByClassName("check-chip")[0].style.display = "";
        textoChip.innerText = data.mensaje;
        pantalla_grabado_chip(data);
    }

}

function pantalla_grabado_chip(data){
    if (!data.status){
        grabar_chip.style.color = 'red';
        circle_primario.style.background = 'red';
        numero_primario.innerText = "X";
        document.getElementsByClassName("check-chip")[0].style.display = "none";
        document.getElementsByClassName("alert-chip")[0].style.display = "";

    }

}

function pantalla_impresion_boleta(){

    cambio_alto_hr()
    document.getElementsByTagName("hr")[0].style.color = "#241A47";
    circle_secundario.style.background = "#241A47";
    imprimir.style.color = "#241A47";
    const textoImpresionBoleta = document.getElementsByClassName("generacion_boletas_prueba-texto_imprimir_boleta")[0];
    textoImpresionBoleta.innerText = constants.i18n.imprimiendo_boleta;
}

function pantalla_resultado_impresion_boleta(data){

    
    if (!data.status){
        imprimir.style.color = 'red';
        circle_secundario.style.background = 'red';
        numero_secundario.innerText = "X";
        document.getElementsByClassName("check-imprimir")[0].style.display = "none";
        document.getElementsByClassName("alert-imprimir")[0].style.display = "";

    }
    else{
        document.getElementsByClassName("check-imprimir")[0].style.display = "";
    }


    cambio_alto_hr()

    const textoImpresionBoleta = document.getElementsByClassName("generacion_boletas_prueba-texto_imprimir_boleta")[0];
    textoImpresionBoleta.innerText = data.mensaje
    change_botton_enable();
    
    hide_elements('.btn_reiniciar');
    hide_elements('.btn_continuar');
    show_elements('.btn_repetir');
    show_elements('.btn_continuar_pantalla');

    const btn_repetir = document.querySelector(".btn_repetir");
    btn_repetir.innerHTML = constants.i18n.btn_repetir;

    const btn_continuar = document.querySelector(".btn_continuar_pantalla");
    btn_continuar.innerHTML = constants.i18n.btn_continiar;

    document.querySelectorAll(".btn_repetir").forEach((btn) => {
        btn.addEventListener("click", () => send("reinicio_pantallas"));
    });

    document.querySelectorAll(".btn_continuar_pantalla").forEach((btn) => {
        btn.addEventListener("click", () => send("paso_pantalla_verificar_imagen"));
    });

}



function pantalla_paso_3(){

    hide_elements('.cdqc_pantalla_grabado_impresion');    
    
    loadImage("img/prueba_equipo/p4_expulsar.png")
    .then( () =>{ 
        progreso_pantalla_paso_3()
    });


}


function progreso_pantalla_paso_3(){

    const p_mensaje = document.getElementsByClassName('mensaje_tooltip-expulsar')[0];
    p_mensaje.innerText = constants.i18n.verificacion_texto_boleta;

    const btn_continuar = document.querySelector('.btn_pantalla_verificar')
    btn_continuar.innerText = constants.i18n.btn_continiar;

    document.querySelectorAll('.btn_pantalla_verificar').forEach((btn) => {
        console.log(btn);
        btn.addEventListener("click", () => send("paso_pantalla_verificar"));
    });   

    show_elements('.cdqc_pantalla_verificacion_boleta');
}


function pantalla_paso_4(){

    hide_elements('.generacion_boletas_prueba');
    hide_elements('.cdqc_pantalla_grabado_impresion');
    hide_elements('.cdqc_pantalla_verificacion_boleta');
    show_elements('.cdqc_pantalla_validacion_rfid');
    hide_elements('.cdqc_pantalla_leyenda_verificacion_chip');
    hide_elements('.cdqc_pantalla_finalizacion_verificacion');
    hide_elements('.popup');
    
    
    change_botton_disabled()

    const html = document.querySelector(".cdqc_pantalla_validacion_rfid")
    const text = html.children[0];

    text.innerText =
    "B. " + constants.i18n.verificacion_boleta_prueba_maquina;

    const p_mensaje = document.querySelector('.mensaje_tooltip-verificar');
    p_mensaje.innerText = constants.i18n.apoye_boleta_antena;

    const img = document.querySelector('.generacion_boletas_prueba-img-verificar');

    if (window.matchMedia("(min-width: 1920px)").matches) {
        img.src = "img/prueba_equipo/p6_verificar.png";
    }
    else{
        img.src = "img/prueba_equipo/p4_verificar.png";
    }

    const TextDescTiempo = document.querySelector('.generacion_boletas-texto_desc_tiempo');
    TextDescTiempo.innerText = constants.i18n.tiempo_disponible;

    temporizador(20, 0);

}


function error_leer_chip(data){

    hide_elements('.cdqc_pantalla_validacion_rfid');
    hide_elements('.cdqc_pantalla_leyenda_verificacion_chip');
    show_elements('.cdqc_pantalla_finalizacion_verificacion');
    hide_elements('.popup');
    hide_elements('.generacion_boletas-texto_lectura_chip');
    hide_elements('.generacion_boletas-ckeck');
    show_elements('.error_chip-alert');
    hide_elements('.generacion_boletas-texto_chip_leido');
    show_elements('.generacion_boletas-texto_error_chip_leido')

    const html = document.querySelector(".cdqc_pantalla_finalizacion_verificacion")
    const text = html.children[0];

    text.innerText =
    "B. " + constants.i18n.verificacion_boleta_prueba_maquina;

    const iconCkeck = document.querySelector('.error_chip-alert');
    iconCkeck.innerText = "";

    const TextChipLeido = document.querySelector('.generacion_boletas-texto_error_chip_leido')
    TextChipLeido.innerText = constants.i18n.error_leer_chip;


    const botonFinalizar = document.querySelector('.btn_finalizar_modulo')
    botonFinalizar.innerText = constants.i18n.btn_finalizar;
    
    document.querySelectorAll(".btn_finalizar_modulo").forEach((btn) => {
        btn.addEventListener("click", () => { 
            event_buttom_finalizar(data);
        });
    });

    const botonRepetir = document.querySelector('.btn_repetir_prueba_verificacion');
    botonRepetir.innerText = constants.i18n.btn_repetir;

    document.querySelectorAll(".btn_repetir_prueba_verificacion").forEach((btn) => {
        btn.addEventListener("click", () => {
            send("cambio_estado_repetir_prueba_validacion")
            btn_confirmar_paso_pantalla()
            
         });
    });

}



function pantalla_paso_5(){

    hide_elements('.cdqc_pantalla_validacion_rfid');
    show_elements('.cdqc_pantalla_leyenda_verificacion_chip');
    hide_elements('.cdqc_pantalla_finalizacion_verificacion');
    hide_elements('.popup');


    const html = document.querySelector(".cdqc_pantalla_leyenda_verificacion_chip")
    const text = html.children[0];

    text.innerText =
    "B. " + constants.i18n.verificacion_boleta_prueba_maquina;
    
    const TextLecChip = document.querySelector('.generacion_boletas_prueba-texto_1')
    TextLecChip.innerText = constants.i18n.leyendo_chip;

    const TextLecChip2 = document.querySelector('.generacion_boletas_prueba-texto_2')
    TextLecChip2.innerText = constants.i18n.no_remueva_boleta;

    send("paso_pantalla_final");

}

function pantalla_paso_6(data){

    hide_elements('.cdqc_pantalla_leyenda_verificacion_chip');
    show_elements('.cdqc_pantalla_finalizacion_verificacion');

    show_elements('.generacion_boletas-ckeck');
    hide_elements('.error_chip-alert');
    show_elements('.generacion_boletas-texto_chip_leido');
    hide_elements('.generacion_boletas-texto_error_chip_leido')

    const html = document.querySelector(".cdqc_pantalla_finalizacion_verificacion")
    const text = html.children[0];

    text.innerText =
    "B. " + constants.i18n.verificacion_boleta_prueba_maquina;

    const iconCkeck = document.querySelector('.generacion_boletas-ckeck');
    iconCkeck.innerText = "";

    const TextChipLeido = document.querySelector('.generacion_boletas-texto_chip_leido');
    TextChipLeido.innerText = constants.i18n.exito_lectura_chip;

    const botonFinalizar = document.querySelector('.btn_finalizar_modulo')
    botonFinalizar.innerText = constants.i18n.btn_finalizar;
    
    document.querySelectorAll(".btn_finalizar_modulo").forEach((btn) => {
        btn.addEventListener("click", () => { 
            event_buttom_finalizar(data);
        });
    });

    const botonRepetir = document.querySelector('.btn_repetir_prueba_verificacion');
    botonRepetir.innerText = constants.i18n.btn_repetir;

    document.querySelectorAll(".btn_repetir_prueba_verificacion").forEach((btn) => {
        btn.addEventListener("click", () => {
            send("cambio_estado_repetir_prueba_validacion")
            btn_confirmar_paso_pantalla()
            
         });
    });


    const botonApagar = document.querySelector('.btn_apagar_equipo');
    botonApagar.innerText = constants.i18n.apagar;

    botonApagar.addEventListener("click", () => {
        cargar_popup_apagar();
    });

}

function event_buttom_finalizar(data){
    console.log(data);
    console.log(data.CDQC_LITE_ISO_GENERICA);
    if (data.CDQC_LITE_ISO_GENERICA) {
        send('reinicio_modulo')
    }else{
        send("salir")
    }
}


function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }


function temporizador(inicio, final) {

    this.inicio = inicio;
    this.contador = this.inicio;
    this.final = final;
    clearInterval(this.idInterval)

    const viewTimer = document.getElementsByClassName('generacion_boletas-tiempo')
    viewTimer[0].innerHTML = "";
    this.idInterval = setInterval(function(){

        if(this.contador == this.final){
            clearInterval(this.idInterval)
            return;
        }
        if (viewTimer.length > 0) {
            viewTimer[0].innerHTML = `${this.contador--} Segundos`;
        }
    }, 1000);

}


function change_botton_enable(){
    const btn = document.querySelector('.btn_continuar')
    document.querySelector('.btn_continuar').disabled = false;
    btn.style.background = "#14B3F4";
    btn.style.color = "#2A2A2B";
}

function change_botton_disabled() {
    const btn = document.querySelector('.btn_continuar')
    btn.disabled = true;
    btn.style.background = "#96D1EA";
    btn.style.color = "#787eaa";
}

function cargar_popup(){

    hide_elements('.cdqc_pantalla_validacion_rfid');
    show_elements('.popup');
    
    const mensaje = document.getElementsByClassName("mensaje-verificacion")[0];
    mensaje.innerText = constants.i18n.tiempo_verificacion_boleta_popup;

    document.querySelectorAll(".btn_confirmar").forEach((btn) => {
        btn.addEventListener("click", () => btn_confirmar_paso_pantalla());
    });

    document.querySelectorAll(".btn_cancelar").forEach((btn) => {
        btn.addEventListener("click", () => btn_cancelar_paso_pantalla());
    });

}

function cargar_popup_apagar(){

    show_elements('.popup');

    const mensaje = document.getElementsByClassName("mensaje-verificacion")[0];
    mensaje.innerText = constants.i18n.esta_seguro_apagar;

    document.querySelectorAll(".btn_confirmar").forEach((btn) => {
        btn.addEventListener("click", () => send("apagar_equipo"));
    });

    document.querySelectorAll(".btn_cancelar").forEach((btn) => {
        btn.addEventListener("click", () => hide_elements(".popup"));
    });

}

function btn_confirmar_paso_pantalla(){
    hide_elements(".popup");
    pantalla_paso_4();
    send("registrar_lector")
    send("confirmacion_popup_validacion_chip")

}

function btn_cancelar_paso_pantalla(){
    hide_elements(".popup");
    send("registrar_lector");
    send("cancelacion_popup_validacion_chip");
    send("paso_cancelar_popup");
    
}

function cambio_alto_hr(){
    if (window.matchMedia("(min-width: 1920px)").matches) {
        document.getElementsByTagName("hr")[0].style.height = "13rem";
    }
    else{
        document.getElementsByTagName("hr")[0].style.height = "7rem";
    }
}

function loadImage(url) {
    return new Promise((resolve) => {
        const image = document.getElementsByClassName('prueba_equipo-container_img_expulsar')[0];
        image.addEventListener('load', () => {
            resolve(image);
        });
        image.src = url; 
    });

}