class HorarioEleccion {
    constructor(inicio, fin) {
        this._fechaHoy = new Date();
        this._fechaInicio = this.desdeHorasMinutosString(inicio);
        this._fechaFin = this.desdeHorasMinutosString(fin);
        if (this._fechaInicio > this._fechaFin)
            throw new Error(
                "Fecha de inicio de elección no puede ser mayor que la fecha de fin."
            );
    }

    inicializarFecha() {
        /*
         * El día no es relevante pero debe elegirse uno. En este caso se usa
         * el día de hoy para evitar parseos de string.
         */
        return new Date(
            this._fechaHoy.getFullYear(),
            this._fechaHoy.getMonth(),
            this._fechaHoy.getDay(),
            0,
            0,
            0,
            0
        );
    }

    horasMinutosEnString(horasMinutosString) {
        return {
            horas: horasMinutosString.split(":")[0],
            minutos: horasMinutosString.split(":")[1],
        };
    }

    desdeHorasMinutosString(horasMinutosString) {
        const { horas, minutos } = this.horasMinutosEnString(
            horasMinutosString
        );
        return this.desdeHorasMinutos(horas, minutos);
    }

    desdeHorasMinutos(horas, minutos) {
        const output = this.inicializarFecha();
        output.setHours(horas);
        output.setMinutes(minutos);
        if (isNaN(output))
            throw new Error(
                `Fecha inválida: no es posible asignar la hora '${horas}:${minutos}'.`
            );
        return output;
    }

    enHorario(horas, minutos) {
        const fechaDada = this.desdeHorasMinutos(horas, minutos);
        return fechaDada >= this._fechaInicio && fechaDada < this._fechaFin;
    }

    esHoraEnHorario(hora) {
        return (
            hora >= this._fechaInicio.getHours() &&
            hora < this._fechaFin.getHours()
        );
    }

    esMinutosEnHorario(minutos) {
        const esMismaHora =
            this._fechaInicio.getHours() === this._fechaFin.getHours();
        const minutosMin = esMismaHora ? this._fechaInicio.getMinutes() : 0;
        const minutosMax = esMismaHora ? this._fechaFin.getMinutes() : 60;
        return minutos >= minutosMin && minutos < minutosMax;
    }

    esFechaTardia(horas, minutos) {
        const fechaDada = this.desdeHorasMinutos(horas, minutos);
        return fechaDada >= this._fechaFin;
    }

    esHoraTardia(hora) {
        return hora >= this._fechaFin.getHours();
    }

    esMinutosTardio(minutos) {
        const esMismaHora =
            this._fechaInicio.getHours() === this._fechaFin.getHours();
        const minutosMin = esMismaHora ? this._fechaFin.getMinutes() : 0;
        const minutosMax = 60;
        return minutos >= minutosMin && minutos < minutosMax;
    }
}

let horarioEleccion = null;

/* exported inicializarHoraEleccion */
function inicializarHoraEleccion({
    hora_apertura,
    min_apertura,
    hora_cierre,
    min_cierre,
}) {
    horarioEleccion = new HorarioEleccion(
        `${hora_apertura}:${min_apertura}`,
        `${hora_cierre}:${min_cierre}`
    );
}

/* exported validarCamposHorarios */
function validarCamposHorarios(modulo, camposVisitados, campoActivo) {
    var elemento_hora = document.getElementsByName("hora")[0];
    var elemento_minutos = document.getElementsByName("minutos")[0];

    limpiarValidaciones([elemento_hora, elemento_minutos]);

    const campoHora = campoHorarioData(
        elemento_hora,
        campoActivo,
        camposVisitados
    );
    const campoMinutos = campoHorarioData(
        elemento_minutos,
        campoActivo,
        camposVisitados
    );

    const validacionesModulos = validacionesDeModulos();

    const esValidoCampoHora = campoHoraEsValido(
        campoHora,
        campoMinutos,
        validacionesModulos[modulo]
    );
    const esValidoCampoMinutos = campoMinutosEsValido(
        campoHora,
        campoMinutos,
        validacionesModulos[modulo]
    );

    elemento_hora.setCustomValidity(esValidoCampoHora ? "" : "Hora no válida");
    elemento_minutos.setCustomValidity(
        esValidoCampoMinutos ? "" : "Minutos no válidos"
    );

    return {
        hora: { ...campoHora, invalido: !esValidoCampoHora },
        minutos: { ...campoMinutos, invalido: !esValidoCampoMinutos },
    };
}

/* exported autopasarCamposDeHorario */
function autopasarCampoDeHorario(horaData, minutosData, onAutopasar) {
    const autopasar_hora = horaData.activo && !horaData.invalido;
    const autopasar_minutos =
        minutosData.activo &&
        !minutosData.invalido &&
        minutosData.valor.length == 2;
    if (autopasar_hora || autopasar_minutos) onAutopasar();
}

const campoHoraEsValido = (campoHora, campoMinutos, validaciones) => {
    const esValidoIndividualmente = () => validaciones.horaValida(campoHora);
    const esValidoEnConjunto = () =>
        validaciones.horarioValido(campoHora, campoMinutos);
    return campoHorarioEsValido(
        campoHora,
        campoMinutos,
        esValidoIndividualmente,
        esValidoEnConjunto
    );
};

const campoMinutosEsValido = (campoHora, campoMinutos, validaciones) => {
    const esValidoIndividualmente = () =>
        validaciones.minutosValido(campoMinutos);
    const esValidoEnConjunto = () =>
        validaciones.horarioValido(campoHora, campoMinutos);
    return campoHorarioEsValido(
        campoMinutos,
        campoHora,
        esValidoIndividualmente,
        esValidoEnConjunto
    );
};

const campoHorarioEsValido = (
    campoAValidar,
    campoComplementario,
    esValidoIndividualmente,
    esValidoEnConjunto
) => {
    if (!campoAValidar.visitado) return true;
    if (campoAValidar.vacio) return false;
    if (campoAValidar.invalido) return false;
    if (campoComplementario.vacio) return esValidoIndividualmente();
    if (campoComplementario.invalido) return false;
    return esValidoEnConjunto();
};

const campoHorarioData = (elemento, activo, camposVisitados) => {
    return {
        valor: elemento.value,
        valorEntero: parseInt(elemento.value),
        vacio: elemento.value === "",
        invalido: !elemento.checkValidity(),
        activo: activo === elemento,
        visitado: camposVisitados.includes(elemento.name),
    };
};

const validacionesDeModulos = () => {
    const apertura = {
        horaValida: (campo) =>
            horarioEleccion.esHoraEnHorario(campo.valorEntero),
        minutosValido: (campo) =>
            horarioEleccion.esMinutosEnHorario(campo.valorEntero),
        horarioValido: (campoHora, campoMinutos) =>
            horarioEleccion.enHorario(
                campoHora.valorEntero,
                campoMinutos.valorEntero
            ),
    };
    const escrutinio = {
        horaValida: (campo) => horarioEleccion.esHoraTardia(campo.valorEntero),
        minutosValido: (campo) =>
            horarioEleccion.esMinutosTardio(campo.valorEntero),
        horarioValido: (campoHora, campoMinutos) =>
            horarioEleccion.esFechaTardia(
                campoHora.valorEntero,
                campoMinutos.valorEntero
            ),
    };
    return { apertura, escrutinio };
};
const limpiarValidaciones = (elementos) => {
    elementos.forEach((elemento) => elemento.setCustomValidity(""));
};
