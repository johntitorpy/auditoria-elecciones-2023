const carga_templates_boleta = async () => {
    return new Promise((resolve, reject) => {
        fetch("boleta_template.html")
            .then(res => res.text())
            .then(templates => {
                const html = document.querySelector("html")
                html.innerHTML += templates
                resolve()
            })
            .catch((error) => reject(error));
    });
}

const crear_row = (index, n_columnas, n_filas, n_secciones, con_troquel) => {

    const vacios = (n_columnas * n_filas) - (n_secciones + 1)
    let n = candidato_maxn(n_secciones)
    const new_row = `<div class="row max${n} ${(con_troquel) ? 'con-troquel' : ''}">`
    const last_row = `<div class="row max${n} ${(con_troquel) ? 'con-troquel' : ''} last_row justify-end">`

    if (index === 0 || index === (n_columnas - vacios) || index === ((n_columnas * 2) - vacios)) {
        if ((index + n_columnas) <= n_secciones)
            return new_row
        else
            return last_row
    }
}

const cerrar_row = (index, n_columnas, n_filas, n_secciones) => {
    const vacios = (n_columnas * n_filas) - (n_secciones + 1)
    if (index === (n_columnas - vacios - 1) ||
        index === ((n_columnas * 2) - vacios - 1) ||
        index === (n_secciones - 1)
    ) {
        return '</div>'
    }
}

const verificar_overflow_boleta = (elementos, overflow, elem) => {
    let error_overflow = false;
    for (let i = 0; i < elementos.length; i++) {
        if (elementos[i].scrollHeight > elementos[i].clientHeight) {
            error_overflow = true;
            elementos[i].style.background = "red";
            if (!Object.keys(overflow).includes('dif_height_' + elem))
                overflow['dif_height_' + elem] = []
            overflow['dif_height_' + elem].push(elementos[i].scrollHeight - elementos[i].clientHeight)
        }
        if (elementos[i].scrollWidth > elementos[i].clientWidth) {
            error_overflow = true;
            elementos[i].style.background = "red";
            if (!Object.keys(overflow).includes('dif_width_' + elem))
                overflow['dif_width_' + elem] = []
            overflow['dif_width_' + elem].push(elementos[i].scrollWidth - elementos[i].clientWidth)
        }
        if (error_overflow)
            break
    }
}

const verificar_overflow_boleta_html = () => {
    console.log('Verificando overflow...')
    const candidatos = document.querySelectorAll(".candidato");
    let overflow = {}
    let elem = 'parent'
    verificar_overflow_boleta(candidatos, overflow, elem);
    for (let i = 0; i < candidatos.length; i++) {
        elem = 'child'
        verificar_overflow_boleta(candidatos[i].childNodes, overflow, elem);
    }
    return overflow
}

const generar_html_boleta = async (data) => {
    let json_data = JSON.parse(data.replaceAll("'", "\""))

    // Parámetro para que los títulos se centren
    // y se aproveche mejor el espacio en la previsualización
    json_data['previsualizacion'] = true
    json_data['troquel'] = false

    const html_boleta = compilar_templates_boleta(json_data)

    const css_boletas = await fetch("css/boleta.css")
        .then(res => res.text())
        .then(css => css)

    return `
        <html>
            <head>
                <style id="estilos_boleta">
                    ${css_boletas}
                </style>  
                ${
                    (typeof overflow_boletas !== 'undefined' && overflow_boletas === true)
                    ? 
                        `<script>
                            const verificar_overflow_boleta = ${verificar_overflow_boleta}
                            const verificar_overflow_boleta_html = ${verificar_overflow_boleta_html}
                    
                            window.onload = () => {
                            const _verified = verificar_overflow_boleta_html()
                            if (_verified && Object.keys(_verified).length !== 0)
                                console.warn(_verified)
                            }
                        </script>` 
                    : 
                        ''
                }              
            </head>
            <body id="boleta">
                <div class="body">
                    ${html_boleta}
                </div>
            </body>
        </html>
    `
}


const generar_iframe_boleta = (tmpl) => {
    var iframe = document.createElement("iframe")
    iframe.classList.add('frame_boleta')
    iframe.setAttribute("id", "frame_boleta")
    iframe.scrolling = "no"
    var blob = new Blob([tmpl], {type: 'text/html'})
    iframe.src = URL.createObjectURL(blob)
    return iframe
}

const inserta_imagen_boleta = async (muestra_html, contenedor, data) => {
    if (muestra_html) {
        registrarHelpersBoleta()
        const tmpl = await generar_html_boleta(data)
        const iframe = generar_iframe_boleta(tmpl)
        contenedor.innerHTML = ''
        contenedor.appendChild(iframe)
        return iframe
    } else {
        const img = decodeURIComponent(data);
        const img_elem = document.createElement("img");
        img_elem.src = img;
        contenedor.innerHTML = ''
        contenedor.appendChild(img_elem)
        return null
    }
}
