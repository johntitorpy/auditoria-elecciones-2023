const ID_CONTENEDOR_PADRE = "tabla";
const ID_TABLA_PREFERENTES = "tabla_preferentes";
const BTN_EXPANDIR_CLASS = "tabla_preferencias-btn_expandir";
const CLASS_CARGO_CON_PREFERENTES = "cargo_con_preferentes";
const CLASS_PANEL_DERECHO = "contenedor-der";
const BTN_EXPANDIR_CONTENT_CLASS = "tabla_preferencias-btn_expandir__span";
const ICONO_EXPANDIDA = "&#xe314;";
const ICONO_CONTRAIDA = "&#xe315;";

const TEMPLATE_TABLA_PREFERENTES = "tabla-preferentes";
const TEMPLATE_DIR_TABLA_PREFERENTES = "pantallas/escrutinio";
const TEMPLATE_CARGO_CON_PREFERENTES = "cargo-con-preferentes-custom";
const TEMPLATE_CARGO_CON_PREFERENTES_CONTRAIDO = "cargo-con-preferentes";
const TEMPLATE_DIR_CARGO_CON_PREFERENTES = "pantallas/escrutinio";

const EXPANDIDA_EN_INICIO = false;
const CARGO_IDX_EN_INICIO = 0;

function hay_preferencias(cargos, { datos_preferencias = null }) {
    const preferencias_en_cargos = () =>
        Object.keys(datos_preferencias).some((i) => cargos.includes(i));
    return datos_preferencias !== null && preferencias_en_cargos();
}

// usa una dependencia externa: generar_titulos (de tabla.js)
function generar_titulos_de_cargos(grupo_cat) {
    return generar_titulos(grupo_cat);
}
class TablaPreferentes {
    constructor(
        expandida_en_inicio = EXPANDIDA_EN_INICIO,
        cargo_visitado_idx_en_inicio = CARGO_IDX_EN_INICIO,
        generar_titulos = generar_titulos_de_cargos
    ) {
        this.expandida_en_inicio = expandida_en_inicio;
        this.cargo_visitado_idx_en_inicio = cargo_visitado_idx_en_inicio;
        this.generar_titulos = generar_titulos;

        this.__inicializar_estados();
        this.__inicializar_panel();
    }

    actualizar(data_a_actualizar) {
        this.__rellenar_html().then(() => {
            this.__inicializar_boton_expandir();
            this.__actualizar_panel(data_a_actualizar);
        });
    }

    __inicializar_estados() {
        let expandida_state = this.expandida_en_inicio;
        this.__set_expandida_state = (expandida) =>
            (expandida_state = expandida);
        this.__get_expandida_state = () => expandida_state;

        let cargo_visitado_idx_state = this.cargo_visitado_idx_en_inicio;
        this.__set_cargo_visitado_idx_state = (cargo_visitado) =>
            (cargo_visitado_idx_state = cargo_visitado);
        this.__get_cargo_visitado_idx_state = () => cargo_visitado_idx_state;
    }

    __inicializar_panel() {
        this.panel_cargos_con_preferentes = new PanelCargosConPreferentes({
            expandido: () => this.__get_expandida_state(),
            cargo_visitado_idx: () => this.__get_cargo_visitado_idx_state(),
            set_cargo_visitado_idx: (cargo_visitado) =>
                this.__set_cargo_visitado_idx_state(cargo_visitado),
            generar_titulos: (grupo_cat) => this.generar_titulos(grupo_cat),
        });
    }

    __rellenar_html() {
        return new Promise((resolve) => {
            fetch_template(
                TEMPLATE_TABLA_PREFERENTES,
                TEMPLATE_DIR_TABLA_PREFERENTES
            ).then((template) => {
                document
                    .getElementById(ID_CONTENEDOR_PADRE)
                    .insertAdjacentHTML("beforeend", template());
                    resolve();
            });
        });
    }

    __actualizar_panel(data) {
        this.panel_cargos_con_preferentes.actualizar(data);
        this.__cambiar_icono_boton_expandir();
    }

    __inicializar_boton_expandir() {
        const expandir_tabla = () => {
            this.__set_expandida_state(!this.__get_expandida_state());
            this.__cambiar_icono_boton_expandir();
            this.__ocultar_panel_derecho();
            this.panel_cargos_con_preferentes.expandir_o_contraer(
                this.__get_expandida_state(),
                this.__get_cargo_visitado_idx_state()
            );
        };

        asignar_event_listener(BTN_EXPANDIR_CLASS, expandir_tabla);

        function asignar_event_listener(
            element_class,
            on_click,
            evento = "click"
        ) {
            document
                .getElementsByClassName(element_class)[0]
                .addEventListener(evento, on_click);
        }
    }

    __cambiar_icono_boton_expandir() {
        const icono = this.__get_expandida_state()
            ? ICONO_EXPANDIDA
            : ICONO_CONTRAIDA;
        document.getElementsByClassName(
            BTN_EXPANDIR_CONTENT_CLASS
        )[0].innerHTML = icono;
    }

    __ocultar_panel_derecho() {
        document.getElementsByClassName(CLASS_PANEL_DERECHO)[0].style.display =
            this.__get_expandida_state() ? "none" : "";
    }
}

class PanelCargosConPreferentes {
    constructor({
        expandido,
        cargo_visitado_idx,
        set_cargo_visitado_idx,
        generar_titulos,
    }) {
        this.__expandido = expandido;
        this.__cargo_visitado_idx = cargo_visitado_idx;
        this.__set_cargo_visitado_idx = set_cargo_visitado_idx;
        this.__generar_titulos = generar_titulos;

        this.__actualizar_data({});
    }

    expandir_o_contraer() {
        this.__render();
    }

    actualizar(data) {
        this.__actualizar_data(data);
        this.__render();
    }

    __actualizar_data(data) {
        this.grupo_cat = data.grupo_cat || null;
        this.tabla_preferentes_data = generar_data_tabla_preferencias(data);
    }

    __render() {
        this.__rellenar_con_html();
        
    }

    __rellenar_con_html() {
        this.__html_cargos_con_preferentes().then((html) => {
            this.__contenedor().innerHTML = html;
            this.__inicializar_los_componentes_de_cargos();
        });
    }

    __inicializar_los_componentes_de_cargos() {
        const cargos_con_preferentes = [
            this.__elementos_cargos_con_preferentes()[0],
        ].map((elemento, idx) => {
            return new CargosConPreferentes({
                elemento: elemento,
                cargos: cargos_de_componente.bind(this)(idx),
                cambio_cargo_callback: on_cambio_cargo.bind(this)(),
                cargo_actual_idx: cargo_actual_de_componente.bind(this)(),
            });
        });

        cargos_con_preferentes.forEach((c) => c.actualizar());

        function cargos_de_componente(idx) {
            const cargos_con_preferentes_ordenados =
                this.__cargos_con_preferentes_ordenados();
            return this.__expandido()
                ? cargos_con_preferentes_ordenados
                : cargos_con_preferentes_ordenados;
        }

        function cargo_actual_de_componente() {
            return this.__cargo_visitado_idx();
        }

        function on_cambio_cargo() {
            return (cargo) => {
                this.__set_cargo_visitado_idx(
                    this.__cargo_idx_from_cargo(cargo)
                );
            };
        }
    }

    __html_cargos_con_preferentes() {
        const template_name = this.__expandido()
            ? TEMPLATE_CARGO_CON_PREFERENTES
            : TEMPLATE_CARGO_CON_PREFERENTES_CONTRAIDO;

        return new Promise((resolve, reject) => {
            fetch_template(
                template_name,
                TEMPLATE_DIR_CARGO_CON_PREFERENTES
            ).then((template_preferentes) => {
                const resultado = this.__expandido()
                    ? html_con_panel_expandido.bind(this)(template_preferentes)
                    : html_con_panel_contraido.bind(this)(template_preferentes);
                resolve(resultado);
            });

        });

        function html_con_panel_contraido(template_preferentes) {
            return template_preferentes({
                filas_preferentes: this.tabla_preferentes_data,
            });
        }

        function html_con_panel_expandido_como_matriz(template_preferentes) {
            return template_preferentes({
                filas_preferentes: this.tabla_preferentes_data,
            });
        }

        function format_data_custom(data) {
            return data.map((e) => {
                let nros_orden = getAllNrosDeOrden(e.listas);
                let lista_matriz = fortmatListas(nros_orden, e.listas);
                let formatMatriz = getFormatMatrix(nros_orden, lista_matriz);
                nros_orden = formatMatriz.nros_orden;
                lista_matriz = formatMatriz.lista_matriz;
                let multitable = formatMatriz.multitable;
                return {
                    ...e,
                    nros_orden: nros_orden,
                    listas_para_matriz: lista_matriz,
                    multitable: multitable,
                };
            });
        }

        function getFormatMatrix(nros_orden, lista_matriz) {
            let multitable = false;
            lista_matriz.sort((a,b) => (parseInt(a.nro_lista) > parseInt(b.nro_lista)) ? 1 
                                    : ((parseInt(b.nro_lista) > parseInt(a.nro_lista)) ? -1 : 0))
            if (nros_orden.length > 23) {
                nros_orden = {
                    nros_orden_menor: nros_orden.slice(0, 24),
                    nros_orden_mayor: nros_orden.slice(24, nros_orden.length),
                };
                multitable = true;
            }
            return { nros_orden, lista_matriz, multitable: multitable };
        }

        function getAllNrosDeOrden(listas) {
            let nros_orden = [];
            listas.forEach((l) => {
                l.preferencias.forEach((preferencia) => {
                    const nro_orden = preferencia.nro_orden.toString();
                    if (nros_orden.indexOf(nro_orden) === -1)
                        nros_orden.push(nro_orden);
                });
            });
            return nros_orden;
        }

        function validateResaltado(resaltado) {
            if (resaltado === "resaltado") {
                return true;
            } else {
                return false;
            }
        }

        function fortmatListas(nros_orden, listas) {
            // [ [nroLista, ...voto de cada numero de orden], ..]
            let fila = [];
            listas.forEach((lista) => {
                let filas_preferentes = { nro_lista: lista.numero.toString() };
                let arr_matriz_menor = [];
                let arr_matriz_mayor = [];
                if (nros_orden.length <= 24) {
                    nros_orden.forEach((nroOrden) => {
                        let preferencia = lista.preferencias.find(
                            (e) => e.nro_orden.toString() === nroOrden
                        );
                        if (preferencia) {
                            arr_matriz_menor.push({
                                voto: parseInt(preferencia.votos),
                                resaltado: preferencia.clase_resaltado,
                            });
                        } else {
                            arr_matriz_menor.push({
                                voto: "-",
                                resaltado: preferencia.clase_resaltado,
                            });
                        }
                    });
                    filas_preferentes.votos = arr_matriz_menor;
                    fila.push(filas_preferentes);
                } else {
                    nros_orden.forEach((nroOrden) => {
                        if (nroOrden <= 24) {
                            let preferencia = lista.preferencias.find(
                                (e) => e.nro_orden.toString() === nroOrden
                            );
                            if (preferencia) {
                                arr_matriz_menor.push({
                                    voto: parseInt(preferencia.votos),
                                    resaltado: preferencia.clase_resaltado,
                                });
                            } else {
                                arr_matriz_menor.push({
                                    voto: "-",
                                    resaltado: preferencia.clase_resaltado,
                                });
                            }
                        } else {
                            let preferencia = lista.preferencias.find(
                                (e) => e.nro_orden.toString() === nroOrden
                            );
                            if (preferencia) {
                                arr_matriz_mayor.push({
                                    voto: parseInt(preferencia.votos),
                                    resaltado: preferencia.clase_resaltado,
                                });
                            } else {
                                arr_matriz_mayor.push({
                                    voto: "-",
                                    resaltado: preferencia.clase_resaltado,
                                });
                            }
                        }
                    });
                    filas_preferentes.votos = {
                        arr_matriz_menor,
                        arr_matriz_mayor,
                    };
                    fila.push(filas_preferentes);
                }
            });
            return fila;
        }

        function html_con_panel_expandido(template_preferentes) {
            this.tabla_preferentes_data = format_data_custom(
                this.tabla_preferentes_data
            );
            return [this.__cargos_con_preferentes_ordenados()[0]].reduce(
                (htmlAcumulado, cargo) => {
                    return (
                        htmlAcumulado +
                        html_con_panel_expandido_como_matriz.bind(this)(
                            template_preferentes,
                            this.tabla_preferentes_data.filter(
                                (c) => c.id === cargo
                            )
                        )
                    );
                },
                ""
            );
        }
    }

    __cargos_con_preferentes_ordenados() {
        return todos_los_cargos
            .bind(this)()
            .filter((cargo) =>
                cargos_con_preferentes.bind(this)().includes(cargo)
            );

        function todos_los_cargos() {
            return this.__generar_titulos(this.grupo_cat);
        }

        function cargos_con_preferentes() {
            return this.tabla_preferentes_data.map((c) => c.id);
        }
    }

    __cargo_idx_from_cargo(cargo) {
        return this.__cargos_con_preferentes_ordenados().findIndex(
            (c) => c === cargo
        );
    }

    __ocultar(ocultar) {
        this.__contenedor().style.display = ocultar ? "none" : "";
    }

    __contenedor() {
        return document.getElementById(ID_TABLA_PREFERENTES);
    }

    __elementos_cargos_con_preferentes() {
        return Array.from(
            document.getElementsByClassName(CLASS_CARGO_CON_PREFERENTES)
        );
    }
}

const tablaPreferentes = new TablaPreferentes();

// donde se arma la data
function generar_data_tabla_preferencias(data) {
    let filter = { id_umv: null };
    let tabla_preferencias = [];

    for (let id_categoria in data.datos_preferencias) {
        let cargo = {
            id: id_categoria,
            nombre: local_data.categorias.one({
                codigo: id_categoria,
            }).nombre,
            listas: [],
        };
        for (let id_umv in data.datos_preferencias[id_categoria]) {
            filter.id_umv = id_umv;
            let candidato_principal = local_data.candidaturas.one(filter);
            let preferencias = data.datos_preferencias[id_categoria][id_umv];
            // genera una copia exacta de un json, incluyendo jsons anidados.
            let lista = JSON.parse(JSON.stringify(candidato_principal.lista));
            lista["nro_orden"] = candidato_principal.lista.orden_absoluto[0];
            lista["preferencias"] = [];

            for (let id_umv_preferencia in preferencias) {
                let votos = preferencias[id_umv_preferencia];
                let nro_orden_preferencia = get_nro_orden(id_umv_preferencia)
                let clase_resaltado = "";
                if (
                    typeof data.seleccion !== "undefined" &&
                    data.seleccion != null &&
                    typeof data.preferencia_elegida[id_categoria] !==
                        "undefined"
                ){
                    clase_resaltado = en_seleccion(data.seleccion, {id_umv: Number(id_umv_preferencia)}) 
                        ? "resaltado"
                        : "";
                }
                
                lista.preferencias.push({
                    id_umv: id_umv_preferencia,
                    nro_orden: nro_orden_preferencia,
                    votos: votos,
                    clase_resaltado: clase_resaltado,
                });
            }
            lista.preferencias.sort((a, b) => (a.nro_orden > b.nro_orden ? 1 : -1));
            cargo.listas.push(lista);
        }
        tabla_preferencias.push(cargo);
    }

    tabla_preferencias.sort((a, b) => (a.nro_orden > b.nro_orden ? 1 : -1));
    return tabla_preferencias;
}

Handlebars.registerHelper("validate", function (value) {
    if (value > 0 && typeof value !== "string") {
        return true;
    } else {
        return false;
    }
});
