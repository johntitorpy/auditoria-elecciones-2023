const compilar_templates_boleta = (json_data) => {
    // Templates fijos
    const raw_header_boleta = document.getElementById(`tmpl_${json_data["flavor"]}/boleta_header`).innerHTML
    const header_template = Handlebars.compile(raw_header_boleta)

    const raw_verificador_boleta = document.getElementById(`tmpl_${json_data["flavor"]}/boleta_verificador`).innerHTML
    const verificador_template = Handlebars.compile(raw_verificador_boleta)

    // Templates tarjetas
    let tarjetas_boleta = ''
    for (const [index, data_seccion] of json_data["secciones"].entries()) {
        const inicio_row = crear_row(
            index,
            json_data["n_columnas"],
            json_data["n_filas"],
            json_data["n_secciones"],
            !!(json_data["troquel"]),
        )
        const fin_row = cerrar_row(index, json_data["n_columnas"], json_data["n_filas"], json_data["n_secciones"])

        if (inicio_row)
            tarjetas_boleta += inicio_row

        const nombre_template = `tmpl_${json_data["flavor"]}/${data_seccion['template']}`
        const raw_tarjeta = document.getElementById(nombre_template).innerHTML

        let template = Handlebars.compile(raw_tarjeta)
        tarjetas_boleta += template({
            ...data_seccion,
            index,
            n_secciones: json_data['n_secciones'],
            n_filas: json_data['n_filas'],
            n_columnas: json_data['n_columnas'],
            troquel: !!json_data["troquel"],
        })

        if (fin_row)
            tarjetas_boleta += fin_row
    }

    let html_boleta = `
        ${header_template(json_data)}
        ${tarjetas_boleta}
        ${verificador_template(json_data)}
    `

    // WaterMark
    if (json_data['watermark']) {
        let raw_watermark_boleta = document.getElementById(`tmpl_${json_data["flavor"]}/boleta_watermark`).innerHTML
        let watermark_template = Handlebars.compile(raw_watermark_boleta)
        html_boleta += `${watermark_template(json_data)}`
    }

    // Troquel
    if (json_data['troquel']) {
        let raw_troquel_boleta = document.getElementById(`tmpl_${json_data["flavor"]}/boleta_troquel`).innerHTML
        let troquel_template = Handlebars.compile(raw_troquel_boleta)
        html_boleta += `${troquel_template(json_data)}`
    }

    return html_boleta
}