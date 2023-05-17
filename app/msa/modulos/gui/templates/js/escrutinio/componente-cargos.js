const BTN_IZQUIERDA_CLASS = "contenedor-boton-izquierda";
const BTN_DERECHA_CLASS = "contenedor-boton-derecha";
const TXT_CARGO_CLASS = "cargo-text";
const DIV_CARGOS_PREFERENTES_CLASS = "cargos-preferentes";
const BTN_DESHABILITADO_CLASS = "deshabilitado";

/**
 * @callback cambio_cargo_callback
 * @description Función que se llama cuando se selecciona un nuevo cargo.
 * @param {String} cargo - Cargo que fue seleccionado.
 */

/**
 * Toma la lista de cargos y prepara los elementos del componente
 * de cargos. Esto es, por ejemplo, asignar a los botones de cambio de cargo
 * las funciones que se llaman cuando se disparan los eventos e inicializa el
 * componente con el primer cargo de la lista.
 *
 * @param {Array[String]} lista_cargos - Lista de cargos, ejemplo ["CNJ", "MNA"]
 * @param {cambio_cargo_callback} cambio_cargo_callback - Función que se llama cuando se selecciona un nuevo cargo.
 */
class CargosConPreferentes {
    constructor({
        elemento,
        cargos,
        cambio_cargo_callback,
        cargo_actual_idx = 0,
    }) {
        this.elemento = elemento;
        this.cargos = cargos;
        this.cambio_cargo_callback = cambio_cargo_callback;
        this.cargo_actual_idx = cargo_actual_idx;

        this.__inicializar();
        this.actualizar();
    }

    actualizar() {
        this.__botonera_cambio_de_cargo.inicializar();
        this.__desplegar_cargo(this.cargos[this.cargo_actual_idx]);
    }

    __inicializar() {
        const desplegar_cargo = desplegador_de_cargo({
            elemento_de_componente: this.elemento,
            cambio_cargo_callback: (cargo) => {
                this.__botonera_cambio_de_cargo.actualizar_segun(cargo);
                this.cambio_cargo_callback(cargo);
            },
        });

        const desplegar_cargo_anterior = asignador_de_cargo(
            this.elemento,
            seleccionador_de_cargo_anterior(this.cargos),
            (cargo) => desplegar_cargo(cargo)
        );

        const desplegar_cargo_siguiente = asignador_de_cargo(
            this.elemento,
            seleccionador_de_cargo_siguiente(this.cargos),
            (cargo) => desplegar_cargo(cargo)
        );

        this.__botonera_cambio_de_cargo = new BotoneraCambioDeCargo({
            cargos: this.cargos,
            elementoDeComponente: this.elemento,
            on_desplegar_anterior: desplegar_cargo_anterior,
            on_desplegar_siguiente: desplegar_cargo_siguiente,
        });

        this.__desplegar_cargo = desplegar_cargo;
    }
}

class BotoneraCambioDeCargo {
    constructor({
        cargos,
        elementoDeComponente,
        on_desplegar_anterior,
        on_desplegar_siguiente,
    }) {
        this.cargos = cargos;
        this.elementoDeComponente = elementoDeComponente;
        this.on_desplegar_anterior = on_desplegar_anterior;
        this.on_desplegar_siguiente = on_desplegar_siguiente;
    }

    inicializar() {
        this.bindear();
        this.desplegar();
    }

    actualizar_segun(cargo) {
        this.__habilitar_segun(cargo);
        this.inicializar();
    }

    bindear() {
        this.__bindear_boton_siguiente();
        this.__bindear_boton_anterior();
    }

    desplegar() {
        this.__todos_los_botones().forEach(
            (btn) =>
                (btn.style.visibility = mas_de_un_cargo(this.cargos)
                    ? ""
                    : "hidden")
        );

        function mas_de_un_cargo(cargos) {
            return cargos.length > 1;
        }
    }

    __bindear_boton_anterior() {
        this.__boton_anterior().removeEventListener(
            "click",
            this.on_desplegar_anterior
        );
        this.__boton_anterior().addEventListener(
            "click",
            this.on_desplegar_anterior
        );
    }

    __bindear_boton_siguiente() {
        this.__boton_siguiente().removeEventListener(
            "click",
            this.on_desplegar_siguiente
        );
        this.__boton_siguiente().addEventListener(
            "click",
            this.on_desplegar_siguiente
        );
    }

    /**
     * @function
     * A partir del cargo seleccionado habilita/deshabilita los botones de
     * cambiar el cargo.
     * Si se seleccionó el último cargo, se deshabilita el boton de siguiente cargo.
     * Si se seleccionó el primer cargo, se deshabilita el boton de anterior cargo.
     *
     * @param {Array[String]} cargo - Cargo que se muestra, ejemplo "CNJ", o
     * "MNA", etc.
     */
    __habilitar_segun(cargo) {
        this.__deshabilitar_todos();

        if (es_primer_cargo(this.cargos))
            this.__habilitar_boton_anterior(cargo);

        if (es_ultimo_cargo(this.cargos))
            this.__habilitar_boton_siguiente(cargo);

        function es_primer_cargo(cargos) {
            return cargo === cargos[0];
        }
        function es_ultimo_cargo(cargos) {
            return cargo === cargos.slice(-1)[0];
        }
    }

    __deshabilitar_todos() {
        this.__todos_los_botones().forEach((btn) =>
            btn.classList.remove(BTN_DESHABILITADO_CLASS)
        );
    }

    __habilitar_boton_anterior() {
        this.__boton_anterior().classList.add(BTN_DESHABILITADO_CLASS);
    }

    __habilitar_boton_siguiente() {
        this.__boton_siguiente().classList.add(BTN_DESHABILITADO_CLASS);
    }

    __boton_anterior() {
        return this.elementoDeComponente.getElementsByClassName(
            BTN_IZQUIERDA_CLASS
        )[0];
    }

    __boton_siguiente() {
        return this.elementoDeComponente.getElementsByClassName(
            BTN_DERECHA_CLASS
        )[0];
    }

    __todos_los_botones() {
        return [this.__boton_anterior(), this.__boton_siguiente()];
    }
}

/**
 * A partir de la lista de cargos devuelve una función que recibe un cargo
 * y se encarga de orquestar las llamadas a las distintas funciones que
 * muestran en pantalla el cargo.
 *
 * @param {Array[String]} lista_cargos - Lista de cargos, ejemplo ["CNJ", "MNA"]
 */
const desplegador_de_cargo = ({
    elemento_de_componente,
    cambio_cargo_callback,
}) => {
    const resetear_scroll = reseteador_de_scroll(elemento_de_componente);
    const scroll_a_celda_resaltada = scrolleador_a_celda_resaltada(
        elemento_de_componente
    );
    return (cargo) => {
        mostrar_preferencias_por_cargo(elemento_de_componente, cargo);
        mostrar_titulo_cargo(elemento_de_componente, cargo);
        resetear_scroll();
        scroll_a_celda_resaltada(cargo);
        cambio_cargo_callback(cargo);
    };

    /**
     * Muestra las listas del cargo ``cargo`` y oculta las demás.
     *
     * @param {String} cargo - Cargo del cual se desea mostrar sus listas.
     */
    function mostrar_preferencias_por_cargo(elemento_de_componente, cargo) {
        const cargos = Array.from(
            elemento_de_componente.getElementsByClassName(
                DIV_CARGOS_PREFERENTES_CLASS
            )
        );
        cargos
            .filter((elemento_cargo) => elemento_cargo.dataset.cargo == cargo)
            .map((elemento_cargo) => (elemento_cargo.style.display = "block"));
        cargos
            .filter((elemento_cargo) => elemento_cargo.dataset.cargo != cargo)
            .map((elemento_cargo) => (elemento_cargo.style.display = "none"));
    }

    /**
     * Muestra en pantalla el cargo ``cargo``.
     *
     * @param {String} cargo - Cargo a mostrar en pantalla.
     */
    function mostrar_titulo_cargo(elemento_de_componente, cargo) {
        const cargo_text = Array.from(
            elemento_de_componente.getElementsByClassName(TXT_CARGO_CLASS)
        );
        if (!cargo_text.length) return;
        cargo_text[0].textContent = cargo;
    }
};

/**
 * Construye una función a partir de la lista de cargos. Dicha función
 * recibe el cargo actualmente desplegado en pantalla y devuelve el cargo siguiente
 * según la lista de cargos.
 *
 * @param {Array[String]} lista_cargos - Lista de cargos, ejemplo ["CNJ", "MNA"]
 * @returns {String} - Cargo siguiente.
 */
const seleccionador_de_cargo_siguiente = (lista_cargos) => (cargo_actual) => {
    const cargo_actual_pos = lista_cargos.indexOf(cargo_actual);
    const cargo_nuevo_pos = cargo_actual_pos + 1;
    if (cargo_nuevo_pos >= lista_cargos.length)
        return lista_cargos[lista_cargos.length - 1];
    return lista_cargos[cargo_nuevo_pos];
};

/**
 * Construye una función a partir de la lista de cargos. Dicha función
 * recibe el cargo actualmente desplegado en pantalla y devuelve el cargo anterior
 * según la lista de cargos.
 *
 * @param {Array[String]} lista_cargos - Lista de cargos, ejemplo ["CNJ", "MNA"]
 * @returns {String} - Cargo anterior.
 */
const seleccionador_de_cargo_anterior = (lista_cargos) => (cargo_actual) => {
    const cargo_actual_pos = lista_cargos.indexOf(cargo_actual);
    const cargo_nuevo_pos = cargo_actual_pos - 1;
    if (cargo_nuevo_pos <= 0) return lista_cargos[0];
    return lista_cargos[cargo_nuevo_pos];
};

/**
 * Acción llamada en la interacción del usuario con los botones de anterior cargo y siguiente cargo.
 *
 * @param {Function} obtener_nuevo_cargo - Función llamada para obtener el cargo, puede ser anterior_cargo o siguiente_cargo.
 * @param {Function} mostrar_nuevo_cargo - Función llamada para desplegar el cargo nuevo en pantalla.
 */
const asignador_de_cargo = (
    componente_cargos,
    obtener_nuevo_cargo,
    mostrar_nuevo_cargo
) => () => {
    mostrar_nuevo_cargo(
        obtener_nuevo_cargo(obtener_titulo_cargo(componente_cargos))
    );

    /**
     * Toma el cargo que está desplegando el componente.
     *
     * @returns {String} Cargo desplegado por el componente.
     */
    function obtener_titulo_cargo(componente_cargos) {
        const cargo_text = Array.from(
            componente_cargos.getElementsByClassName(TXT_CARGO_CLASS)
        );
        if (!cargo_text.length) return "";
        return cargo_text[0].textContent;
    }
};

function reseteador_de_scroll(componente_cargos) {
    const SCROLL_STEP = 50;
    const btn_scroll_arriba = componente_cargos.querySelector(
        ".contenedor-scroll.arriba"
    );
    const btn_scroll_abajo = componente_cargos.querySelector(
        ".contenedor-scroll.abajo"
    );
    const elemento_a_scrollear = componente_cargos.querySelector(
        ".cargo_con_preferentes-main"
    );
    return () => {
        habilitar_y_bindear();
    };

    function habilitar_y_bindear() {
        habilitar();
        bindear();
    }

    function habilitar() {
        habilitar_scroll_hacia_arriba();
        habilitar_scroll_hacia_abajo();
    }

    function bindear() {
        bindear_scroll_arriba();
        bindear_scroll_abajo();
        bindear_elemento_a_scrollear();
    }

    function habilitar_scroll_hacia_arriba() {
        asignar_classname(btn_scroll_arriba, subir_esta_deshabilitado());
    }

    function habilitar_scroll_hacia_abajo() {
        asignar_classname(btn_scroll_abajo, bajar_esta_deshabilitado());
    }

    function bindear_scroll_arriba() {
        btn_scroll_arriba.removeEventListener("click", scroll_arriba);
        if (!subir_esta_deshabilitado())
            btn_scroll_arriba.addEventListener("click", scroll_arriba);
    }

    function bindear_scroll_abajo() {
        btn_scroll_abajo.removeEventListener("click", scroll_abajo);
        if (!bajar_esta_deshabilitado())
            btn_scroll_abajo.addEventListener("click", scroll_abajo);
    }

    function bindear_elemento_a_scrollear() {
        elemento_a_scrollear.removeEventListener("scroll", habilitar_y_bindear);
        elemento_a_scrollear.addEventListener("scroll", habilitar_y_bindear);
    }

    function asignar_classname(btn, deshabilitado) {
        btn.classList.toggle(BTN_DESHABILITADO_CLASS, deshabilitado);
    }

    function bajar_esta_deshabilitado() {
        return (
            elemento_a_scrollear.scrollHeight -
                elemento_a_scrollear.scrollTop ===
            height(elemento_a_scrollear)
        );

        function height(element) {
            return element.getBoundingClientRect().height;
        }
    }

    function subir_esta_deshabilitado() {
        return elemento_a_scrollear.scrollTop === 0;
    }

    function scroll_arriba() {
        elemento_a_scrollear.scrollTop =
            elemento_a_scrollear.scrollTop - SCROLL_STEP;
    }

    function scroll_abajo() {
        elemento_a_scrollear.scrollTop =
            elemento_a_scrollear.scrollTop + SCROLL_STEP;
    }
}

function scrolleador_a_celda_resaltada(componente_cargos) {
    return (cargo) => {
        set_scroll(0);
        const celda_resaltada = seleccionar_celda_resaltada();
        if (!celda_resaltada) return;
        set_scroll(posicion_celda_resaltada());

        function seleccionar_celda_resaltada() {
            return componente_cargos.querySelector(
                `[data-cargo=${cargo}] .resaltado`
            );
        }

        function posicion_celda_resaltada() {
            const offset = 87;
            return (
                celda_resaltada.getBoundingClientRect().top +
                window.scrollY -
                offset
            );
        }

        function set_scroll(valor) {
            componente_cargos
                .querySelector(`.cargo_con_preferentes-main`)
                .scroll({
                    top: valor,
                });
        }
    };
}
