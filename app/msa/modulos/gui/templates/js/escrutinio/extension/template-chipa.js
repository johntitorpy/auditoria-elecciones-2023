
class TemplateChipa extends Templates {
    constructor() {
        super();

        //registramos helpers particulares del flavor chipa
        const cargos_con_presidenta = ['DNM'];
        const es_presidenta = (cargo) => cargos_con_presidenta.includes(cargo);
        Handlebars.registerHelper("es_presidenta", es_presidenta);
        
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
                id: "pre_vice",
                template_name: "escrutinio_confirmacion_pre_vice",
                templete_dir
            },
            {
                id: "escrutinio_secundarios",
                template_name: "escrutinio_confirmacion_con_secundarios",
                templete_dir
            },
            {
                id: "escrutinio_secundarios_y_preferentes",
                template_name: "escrutinio_confirmacion_con_secundarios_y_preferentes",
                templete_dir
            },
            {
                id: "escrutinio_con_preferentes",
                template_name: "escrutinio_confirmacion_con_preferentes",
                templete_dir
            },
            {
                id: "escrutinio_sin_preferentes",
                template_name: "escrutinio_confirmacion_sin_preferentes",
                templete_dir
            },
        ];
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
            const tiene_secundarios = es_cargo_con_secundarios(
                candidato.cod_categoria
            );
            const tiene_preferentes = es_candidato_con_preferentes(candidato);
            const pre_vice = es_cargo_pre_vice(candidato.cod_categoria);
            if(es_blanco(candidato)) return "blanco";
            if (pre_vice) return "pre_vice";
            if (tiene_secundarios && tiene_preferentes) return "escrutinio_secundarios_y_preferentes";
            if (tiene_secundarios) return "escrutinio_secundarios";
            if (tiene_preferentes) return "escrutinio_con_preferentes";

            return "escrutinio_sin_preferentes";
        }

        function es_blanco(candidato) {
            return candidato.blanco || candidato.clase === "Blanco";
        }

        function es_candidato_con_preferentes(candidato) {
            return !candidato.cargo_ejecutivo;
        }
    
        function es_cargo_pre_vice(cargo) {
            const cargos_con_presidente_vicepresidente = [
                "PRE", "PRC", "PR3", "PVC", "PVD", "PVN", "DNM", "PVT"
            ];
            return cargos_con_presidente_vicepresidente.includes(cargo);
        }
    
        function es_cargo_con_secundarios(cargo) {
            const cargos_con_secundarios = ["PR2", "PVJ"];
            return cargos_con_secundarios.includes(cargo);
        }
    }

}

templateClass = new TemplateChipa();