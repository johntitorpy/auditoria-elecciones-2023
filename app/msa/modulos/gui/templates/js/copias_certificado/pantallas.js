function pantalla_seleccion_acta(template_data) {
    hide_all();
    const promise_template = fetch_template("seleccion_acta", "pantallas/copias_certificado");
    const promise_popup = fetch_template("popup", "pantallas/copias_certificado");

    Promise.all([
        promise_template,
        promise_popup
    ]).then(([template, template_popup]) => {

        const html_pantallas = template(template_data);
        const html_popup = template_popup();
        document.querySelector('#contenedor_pantallas').innerHTML = html_pantallas;
        document.querySelector('.popup-box').innerHTML = html_popup;

        document.getElementById("_txt_encabezado_copias").innerText =
        constants.i18n.copias_encabezado_seleccionar_acta;

        document.querySelectorAll(".tipo_acta_copia-button").forEach((btn) => {
            btn.addEventListener("click", () => seleccionaActa(btn.value));
        });

        set_on_ir_atras(salir);
        

        function seleccionaActa(tipo_acta) {
            seleccionar_acta_a_copiar(tipo_acta);
        }
    });
    
    //hide_elements(".barra-titulo");
    hide_dialogo();
    show_elements("#contenedor_izq");
    show_elements("#contenedor_opciones");
    show_elements(".contenedor-datos");
}

function pantalla_carga_recuento(data) {
    hide_all();
    const promise_template = fetch_template("carga_recuento", "pantallas/copias_certificado");
    const promise_popup = fetch_template("popup", "pantallas/copias_certificado");
    const acta_a_apoyar = constants.acta_a_apoyar[data.acta_a_copiar];
    Promise.all([
        promise_template,
        promise_popup
    ]).then(([template, template_popup]) => {
        const html_pantallas = template();
        const html_popup = template_popup();
        document.querySelector('#contenedor_pantallas').innerHTML = html_pantallas;
        document.querySelector('.popup-box').innerHTML = html_popup;

        let img_svg = "";
        if(data.acta_a_copiar=="certificado"){
            img_svg = "<img src='img/recuento.png'>";

            document.querySelector("#carga_recuento-texto").innerText =
                constants.i18n.acerque_acta_cierre;
        }else{
            img_svg = `<img src='img/${acta_a_apoyar}.png'>`;
            
            document.querySelector("#carga_recuento-texto").innerText =
                constants.i18n.copias_ayuda_ingresar_acta;
                console.log(constants.i18n.copias_ayuda_ingresar_acta);
        }

        document.querySelector("#_txt_encabezado_copias").innerText =
            constants.i18n.copias_encabezado_ingresar_acta;

        document.querySelector('#svg_cierre').innerHTML = img_svg;
        set_on_ir_atras(pantalla_anterior_carga_recuento);
    });
    
    hide_dialogo();
    show_elements("#contenedor_izq");
    show_elements("#contenedor_opciones");
    show_elements(".contenedor-datos");
}

function pantalla_anterior_carga_recuento() {
    if(constants.actas_a_copiar.length==1)
        set_on_ir_atras(salir);
    else
        seleccionar_acta_a_copiar();
}

function set_on_ir_atras(on_ir_atras) {
    const btn_element = document.querySelector("#accesibilidad li");
    clear_acciones_atras(btn_element);
    btn_element.addEventListener("click", on_ir_atras);

    function clear_acciones_atras(btn_element) {
        const acciones_on_salir = [
            salir,
            pantalla_anterior_carga_recuento,
            pantalla_seleccion_acta,
            pantalla_carga_recuento,
        ];
        acciones_on_salir.forEach((accion) => {
            btn_element.removeEventListener("click", accion);
        });
    }
}
