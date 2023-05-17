const max_cargos = [1, 2, 3, 5, 7, 8, 11, 14, 17]

const candidato_maxn = (n_secciones) => {
    if (max_cargos.includes(n_secciones)) {
        return n_secciones
    } else {
        let max = 0
        let i = 0
        while (max === 0) {
            if (max_cargos[i] > n_secciones)
                max = max_cargos[i]
            i++
        }
        return max
    }
}

const agrandar_seccion = (index, n_columnas, n_filas, n_secciones) => {
    const vacios = (n_columnas * n_filas) - (n_secciones + 1)
    return (vacios > 0) ? index < vacios : false
}

const recorrer_nombre_candidatos_principales = (arr) => {
    let candidatos = ''
    arr.forEach(nombre => {
        candidatos += `
                <div class="candidato_lista_sin_imagen-candidato_principal">${nombre}</div>
            `
    })
    return new Handlebars.SafeString(candidatos)
}

const recorrer_nombre_candidatos_principales_preferencia = (arr) => {
    let candidatos = ''
    arr.forEach(nombre => {
        candidatos += `
            <div class="candidato_lista_sin_imagen-candidato_principal">${nombre}</div>
        `
    })
    return new Handlebars.SafeString(candidatos)
}

const recorrer_nombre_candidatos_secundarios = (arr) => {
    console.log(arr)
    const n_candidatos = arr.length
    let candidatos = ''
    if (n_candidatos > 1)
        arr.forEach((c, i) => {
            if (n_candidatos !== (i + 1))
                c += "; "
            candidatos += `<span class="candidato_lista_sin_imagen-candidato_secundario">${c}</span>`
        })
    else
        candidatos += `<span class="candidato_lista_sin_imagen-candidato_secundario">${arr[0]}</span>`
    return new Handlebars.SafeString(candidatos)
}

const recorrer_nombre_candidatos_suplentes = (arr) => {
    const n_candidatos = arr.length
    let candidatos = ''
    if (n_candidatos > 1)
        arr.forEach((c, i) => {
            if (n_candidatos !== (i + 1))
                c += "; "
            candidatos += `<span class="candidato_lista_sin_imagen-candidato_suplentes">${c}</span>`
        })
    else
        candidatos += `<span class="candidato_lista_sin_imagen-candidato_suplentes">${arr[0]}</span>`
    return new Handlebars.SafeString(candidatos)
}

const ajustar_tamano = (numero_lista) => {
    if (numero_lista.length > 3)
        return "fs-numero-largo"
    else
        return ""
}

const es_primer_cargo = (index) => {
    return index === 0;
}

const es_preferencia = (usa_preferencia, secundarios) => {
    if (usa_preferencia) {
        return false;
    }
    return secundarios !== undefined;
}

const dibujar_watermark = (arr) => {
    let watermarks = ''
    arr.forEach(e => {
        watermarks += `
                <text x="${e[0]}" 
                      y="${e[1]}" 
                      transform="rotate(-40 800, 0)" 
                      style="font-size:${e[3]}px;stroke:#ffffff;stroke-width:1px;">
                      ${e[2]}
                </text>`
    })
    return new Handlebars.SafeString(watermarks)
}

const dibujar_troquel = (troquel, sub_troquel) => {
    let texto = `
            <text x="${troquel[0]}" 
                  y="${troquel[1]}" 
                  transform="rotate(270 110, 0)" 
                  style="font-size:${troquel[3]}px;">
                  ${troquel[2]}
            </text>
            <text x="${sub_troquel[0]}" 
                  y="${sub_troquel[1]}" 
                  transform="rotate(270 110, 0)" 
                  style="font-size:${sub_troquel[3]}px;">
                  ${sub_troquel[2]}
            </text> 
        `
    return new Handlebars.SafeString(texto)
}

const registrarHelpersBoleta = () => {
    Handlebars.registerHelper('candidato_maxn', candidato_maxn)
    Handlebars.registerHelper('agrandar_seccion', agrandar_seccion)
    Handlebars.registerHelper('recorrer_nombre_candidatos_principales', recorrer_nombre_candidatos_principales)
    Handlebars.registerHelper(
        'recorrer_nombre_candidatos_principales_preferencia',
        recorrer_nombre_candidatos_principales_preferencia
    )
    Handlebars.registerHelper('recorrer_nombre_candidatos_secundarios', recorrer_nombre_candidatos_secundarios)
    Handlebars.registerHelper('recorrer_nombre_candidatos_suplentes', recorrer_nombre_candidatos_suplentes)
    Handlebars.registerHelper('ajustar_tamano', ajustar_tamano)
    Handlebars.registerHelper('es_primer_cargo', es_primer_cargo)
    Handlebars.registerHelper('es_preferencias', es_preferencia)
    Handlebars.registerHelper('dibujar_watermark', dibujar_watermark)
    Handlebars.registerHelper('dibujar_troquel', dibujar_troquel)
}