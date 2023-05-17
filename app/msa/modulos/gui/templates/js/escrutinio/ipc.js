/**
 * @namespace js.escrutinio.ipc
 */
var constants = null;

get_url = get_url_function("voto");

/**
 * Envia la señal "document_ready" al backend.
 */
function load_ready_msg() {
    send("document_ready");
}

/**
 * Establece las constantes que llegan desde el backend.
 *
 * @param {*} data - un objeto con las constantes.
 */
function set_constants(data) {
    constants = data;
    const promise_templates_escrutinio = load_templates_escrutinio();
    Promise.all([promise_templates_escrutinio])
    .then(([templates_escrutinio]) => {
            const promise_encabezado = fetch_template("encabezado_chico");
            //cargo primero las extensiones js por que patio las necesita
            load_extension_js(constants.flavor)
            .then(() => {})
            .catch((error) => console.error(error))
            .finally(() => {
                const promise_colores = fetch_template(
                    "colores",
                    "pantallas/escrutinio"
                );
                const promise_patio = load_patio();
                
                Promise.all([promise_encabezado, promise_colores, promise_patio]).then(
                    ([template_encabezado, template_colores, data_patio]) => {
                        pantalla_loader();
                        popular_encabezado(template_encabezado);
                        registrar_helper_colores(template_colores);
                        registrar_helper_i18n();
                        registrar_helper_imagenes();
                        place_text(data.i18n);
                        place_text(data.encabezado);
                        if (!constants.mostrar_cursor) {
                            document.querySelector("body").style.cursor = "none";
                        }
                        load_css(constants.flavor);
    
                        /**
                         * @todo: ¿Por qué se usa un timer aquí? es probable que no sea necesario y
                         * es deseable quitarlo para reducir la complejidad en la carga de la aplicación.
                         */
                        setTimeout(function () {
                            send("cargar_cache");
                        }, 300);
                    }
                );
            });
        })
        .catch((error) => console.error(error));
}

/**
 * Avisa al backend que tiene que lanzar el sonido de tecla apretada.
 */
const sonido_tecla = () => {
    send("sonido_tecla");
};

/**
 * Carga el templates de escrutinio al DOM.
 * Esta función carga todos los templates en memoria.
 */
function load_templates_escrutinio() {
    return new Promise((resolve, reject) => {
        if (constants.templates_compiladas) {
            const url_templates_flavor = 
                constants.PATH_TEMPLATES_FLAVORS + constants.flavor + "/escrutinio/templates.html";
            var url_templates_escriutinio = constants.PATH_TEMPLATES_VAR + "escrutinio.html";
            Promise.all([
                load_template_comp(url_templates_flavor),
                load_template_comp(url_templates_escriutinio)
            ]).then(() => {
                cargar_templates_en_dom();
                resolve();
            });
        } else {
            resolve();
        }
    });
}
