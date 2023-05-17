class TemplateEmpanada extends Templates {
    /**
     * Crea el boton para una lista.
     *
     * @param {*} boleta - un objeto con la informacion de la lista para la que se quiere crear el item de lista.
     * @param {Boolean} normal - Si el id de candidatura está en la boleta o dentro de la lista de la boleta.
     * @returns {*}
     *  @override
     */
      crear_item_lista(boleta, normal, preagrupada) {
        let template_data = this.__get_template_data_lista(boleta, normal, preagrupada);
        let template_name = this.__get_template_name_lista(template_data);
        const template = get_template_desde_cache(template_name);
        var item = template(template_data);
        return item;
    }

    /**
     * Devuelve el nombre del template para las listas
     * @override
     */
    __get_template_name_lista(template_data) {
        const es_lista_completa =
            !template_data.normal 
            && !template_data.preagrupada;
        const es_adhesion = 
            template_data.normal 
            && template_data.preagrupada;
        if (es_lista_completa) return "seleccion_lista_completa";
        if (es_adhesion) return "seleccion_adhesion";
        return "seleccion_adhesion";
    }
    /*
    *
     * Devuelve los datos que necesita el template de lista
     *  @override
     */
    __get_template_data_lista(boleta, normal, preagrupada) {
        var id_lista = "lista_";
        if (normal) {
            id_lista += boleta.lista.id_candidatura;
        } else {
            id_lista += boleta.id_candidatura;
        }

        var seleccionado = "";
        if (this.__modo == "BTN_COMPLETA" && _categorias !== null) {
            if (_lista_seleccionada == boleta.lista.codigo) {
                seleccionado = "seleccionado";
            }
        }
        var candidatos = get_candidatos_boleta(boleta);
        let template_data = this.__main_dict_base(id_lista);
        template_data.lista = normal ? boleta.lista : boleta;
        template_data.normal = normal;
        template_data.seleccionado = seleccionado;
        template_data.candidatos = candidatos;
        template_data.cantidad_candidatos = candidatos.length;
        template_data.preagrupada = preagrupada;
        template_data.agrupacion_municipal = normal && boleta.agrupacion_municipal;
        return template_data;
    }
}

templateClass = new TemplateEmpanada(get_modo(), constants);