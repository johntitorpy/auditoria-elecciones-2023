class TemplateEmpanada extends Templates {
        
    /**
     * Devuelve los componentes de escrutinio que usa el flavor
     */
    __get_componentes_escrutinio() {
        const templete_dir = constants.flavor;;
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
            }
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
            return es_blanco(candidato)
                ? "blanco"
                : "candidato_elegido";
        }

        function es_blanco(candidato) {
            return candidato.blanco || candidato.clase === "Blanco";
        }
    }
}

templateClass = new TemplateEmpanada();