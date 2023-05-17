var template_boleta, template_css;  // Defino variables globales

window.onload = async () => {
    await carga_templates_boleta()
    registrarHelpersBoleta()

    // let raw_template = document.getElementById("tmpl_boleta/boleta").innerHTML
    // window.template_boleta = Handlebars.compile(raw_template)

    fetch('/listo_p_renderizar')
}

const render = async (data) => {
    data = JSON.parse(data)

    let _boleta = document.querySelector("#boleta>.body")
    _boleta.innerHTML = compilar_templates_boleta(data)

    if (!!data['troquel']) {
        document.getElementById("boleta").classList.add("con-troquel")
    } else {
        document.getElementById("boleta").classList.remove("con-troquel")
    }

    if (data.verificar_overflow) {
        let _verified = verificar_overflow_boleta_html();
        if (_verified && Object.keys(_verified).length !== 0) {
            _verified['cod_datos'] = data.id_seleccion
            fetch('/error_overflow/' + JSON.stringify(_verified))
        }
    }

    html2canvas(_boleta, {
        width: 2300,
        height: 832,
        foreignObjectRendering: true,
        windowWidth: 2300,
        windowHeight: 832,
        logging: false
    }).then(canvas => {
        fetch('/imagen_cargada/' + canvas.toDataURL('image/png'))
    })
}
