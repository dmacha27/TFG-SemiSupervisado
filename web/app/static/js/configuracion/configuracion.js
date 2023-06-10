/**
 *
 * Deshabilita/habilita un elemento por su ID.
 * Es utilizado en Self-Training pues este algoritmo permite
 * inicializarse mediante un número de iteraciones máximas o
 * un límite (o threshold). Si el usuario introduce un valor en las
 * iteraciones, el límite se deshabilita (y viceversa), y si el usuario elimina el valor,
 * el límite se habilita (y viceversa).
 *
 * @param value - valor del placeholder
 * @param id - id del elemento a deshabilitar/habilitar
 */
function limitarUnicoMetodoST(value,id){
    document.getElementById(id).disabled = !!value;
}

/**
 *
 * Deshabilita los controles para seleccionar las componentes
 * X e Y dependiendo del checkbox del PCA.
 *
 * @param checked - estado del checkbox del PCA (true o false)
 * @param x - id del selector de la componente x
 * @param y - id del selector de la componente y
 */
function componentesPCA(checked,x,y){
    if (checked) {
        document.getElementById(x).disabled = true;
        document.getElementById(y).disabled = true;
    }else{
        document.getElementById(x).disabled = false;
        document.getElementById(y).disabled = false;
    }
}

/**
 * Genera el formulario de los parámetros de un clasificador
 * base (scikit-learn)
 *
 * @param clasificador - nombre del clasificador base
 * @param div - el <div> destino donde almacenar el formulario
 * @param div_clasificador - id del selector del clasificador base
 */
function generarFormParametros(clasificador, div, div_clasificador) {
    // todos_parametros contiene los parámetros que admite el clasificador
    // así como su estructura (select, number, min, max...)
    const parametros = Object.keys(todos_parametros[clasificador]);
    div.innerHTML = '';

    if (!parametros.length){
        div.style.visibility = "hidden";
    }else {
        div.style.visibility = "visible";
        for (const p of parametros) {

            let parametro = todos_parametros[clasificador][p];
            const label = document.createElement('label');
            label.textContent = parametro.label;

            if (parametro.type === 'select') {
                const select = document.createElement('select');
                select.classList.add('form-select');
                select.name = div_clasificador + "_" + p;

                for (const opcion of parametro.options) {
                    const option = document.createElement('option');
                    option.value = opcion;
                    option.text = opcion;
                    select.appendChild(option);
                }
                select.value = parametro.default;
                div.appendChild(label);
                div.appendChild(select);

            } else {
                const input = document.createElement('input');
                input.type = parametro.type;
                input.step = parametro.step;
                input.min = parametro.min;
                input.max = parametro.max;
                input.name = div_clasificador + "_" + p;
                input.classList.add('form-control');
                input.value = parametro.default;
                div.appendChild(label);
                div.appendChild(input);
            }

        }
    }
}

/**
 *
 * Actualiza el porcentaje de datos en el badge con
 * respecto el rango.
 *
 * @param valor - valor actual del rango
 * @param id_badge - identificador del badge
 */
function actualizarBadgePorcentaje(valor, id_badge) {
    let badge = document.getElementById(id_badge);

    badge.innerHTML = valor.toString()+"%";

}