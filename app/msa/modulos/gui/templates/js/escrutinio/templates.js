let templateClass;

class Templates {
    /**
     * Genera los paneles de confirmacion.
     * 
     * @param {*} data - Datos de la selección.
     * @returns {String} Html en formato de cadena de caracteres.
     */
    generar_paneles_confirmacion(data) {
        return new Promise((resolve, reject) => {
            fetch_template(
                "escrutinio_confirmacion_tarjeta",
                "pantallas/escrutinio"
            ).then((template_tarjeta) => {
                var html = "";
                this.__get_templates_componentes_escrutinio().then((componentes) => {
                    // Renderizo el template para cada uno de los candidatos.
                    for (var i in data.seleccion) {
                        let datos_candidato = data.seleccion[i];
                        //renderiza la primer preferencia
                        const id_umv = (datos_candidato.constructor === Array)
                            ? datos_candidato[0]
                            : datos_candidato;
                        let candidato = local_data.candidaturas.one({id_umv: id_umv});
                        
                        let categoria = local_data.categorias.one({
                            codigo: candidato.cod_categoria,
                        });
                        if (categoria.adhiere == null) {
                            let template_data = 
                                this.__get_template_data_confirmacion(
                                    data.seleccion, 
                                    candidato, categoria, 
                                    data.datos_tabla,
                                    data.datos_preferencias);

                            //registra el componente del candidato antes de llamarlo en el template
                            let componente = 
                                this.__seleccionar_componente_confirmacion(
                                    componentes,
                                    candidato,
                                    categoria);

                            Handlebars.registerPartial(
                                "componenteEscrutinioConfirmacion",
                                componente.template
                            );
                            html += template_tarjeta(template_data);
                        }
                    }
                    resolve(html);
                });
            });
        });
    }

    /**
     * Devuelve los componentes de escrutinio que usa el flavor
     */
    __get_componentes_escrutinio() {
        const templete_dir = constants.flavor;
        return [
            {
                id: "blanco",
                template_name: "escrutinio_confirmacion_blanco",
                templete_dir
            },
            {
                id: "candidato_elegido",
                template_name: "escrutinio_confirmacion_candidato",
                templete_dir
            },
            {
                id: "consulta_popular",
                template_name: "escrutinio_confirmacion_consulta_popular",
                templete_dir
            },
        ];
    }

    /**
     * Devuelve los diferentes componentes de confirmacion que usan los candidatos.
     * instanciando el template para c/u
     * 
     * @returns {Promise}
     */
    __get_templates_componentes_escrutinio() {
        const componentes_escrutinio = this.__get_componentes_escrutinio();
        
        return new Promise((resolve) => {
            const promises_componentes_templates = componentes_escrutinio.map(
                (c) => fetch_template(c.template_name, c.templete_dir)
            );
            Promise.all(promises_componentes_templates).then((templates) => {
                const resultado = inyectar_templates_a_componentes(
                        templates,
                        componentes_escrutinio
                    );
                resolve(resultado);
            });
        });

        
        function inyectar_templates_a_componentes(
            templates,
            componentes_escrutinio
        ) {
            return templates.map((template, idx) => {
                return {
                    ...componentes_escrutinio[idx],
                    template,
                };
            });
        }
    }

    /**
     * Selecciona el template del componente según el candidato y la categoría
     * para esto se necesita que el template este cargado en los componentes
     * 
     * @param {*} componentes_templates - Todos los componentes de escrutinio
     * @param {*} candidato - candidato que se quiere renderizar
     * @param {*} categoria - categoría que se quiere renderizar
     */
    __seleccionar_componente_confirmacion(componentes_templates, candidato, categoria) {
        const id = template_id(candidato, categoria);
        return componentes_templates.find((ct) => ct.id === id);


        function template_id(candidato, categoria) {
            return es_blanco(candidato)
                ? "blanco"
                : es_consulta_popular(categoria)
                ? "consulta_popular"
                : "candidato_elegido";
        }

        function es_blanco(candidato) {
            return candidato.blanco || candidato.clase === "Blanco";
        }

        function es_consulta_popular(categoria) {
            return categoria.consulta_popular;
        }
    }

     /**
     * Devuelve los datos que necesita el template de la tarjeta de confirmacion
     * 
     * @param {*} seleccion - Candidatos seleccionados
     * @param {*} candidato - El candidato a crearle el botón.
     * @param {*} categoria - La categoria a crearle el botón.
     * @param {*} votos - Votos registrados por candidato principal
     * @param {*} votos - Votos registrados por preferente
     * @returns {*}
     */
     __get_template_data_confirmacion(seleccion, candidato, categoria, votos, votos_preferencias) {
        var es_blanco = candidato.clase === "Blanco";
        var img_path = "imagenes_candidaturas/" + constants.juego_de_datos + "/";
        // Secundarios
        let secundarios = null;
        let limitar_candidatos = constants.limitar_candidatos;
        // Si la setting existe
        if (limitar_candidatos !== undefined) {
            let cantidad_secundarios = limitar_candidatos.secundarios;
            // Si hay una cantidad establecida en la setting
            if (cantidad_secundarios !== null) {
                secundarios = candidato.secundarios.slice(0,cantidad_secundarios);
                secundarios = secundarios ? secundarios.join("; ") : "";
            }
        }
        // Si no se limitaron candidatos secundarios por la setting
        // entonces van todos
        if (secundarios === null) {
            secundarios = candidato.secundarios
                ? candidato.secundarios.join("; ")
                : "";
        }

        // Genero los datos para mandarselos al template.
        var data = {};
        data.candidato = candidato;
        data.categoria = categoria;
        data.palabra_lista = constants.i18n.palabra_lista;
        data.es_blanco = es_blanco;
        data.consulta_popular = categoria.consulta_popular
            ? "consulta_popular"
            : "";
        data.no_muestra_lista = categoria.consulta_popular || es_blanco;
        data.muestra_foto = !(categoria.consulta_popular && !es_blanco);
        data.total_candidatos = seleccion.length;
        data.color = !es_blanco ? candidato.lista.color : "";
        data.secundarios = secundarios;
        data.img_path = img_path;
        if(categoria.preferente && ! es_blanco){
            const candidato_principal = get_candidato_principal(candidato);
            data.votos = votos[candidato_principal.id_umv];
            data.votos_preferencia = 
                votos_preferencias[categoria.codigo][candidato_principal.id_umv][candidato.id_umv];
        }else{
            data.votos = votos[candidato.id_umv];
        }
        return data;
     }
}