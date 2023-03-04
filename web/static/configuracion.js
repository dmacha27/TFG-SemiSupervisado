function limitarUnicoMetodoST(value,id){
    document.getElementById(id).disabled = !!value;
}

function componentesPCA(checked,x,y){
    if (checked) {
        document.getElementById(x).disabled = true;
        document.getElementById(y).disabled = true;
    }else{
        document.getElementById(x).disabled = false;
        document.getElementById(y).disabled = false;
    }
}

function generarFormParametros(algoritmo, div) {
    const parametros = Object.keys(todos_parametros[algoritmo]);
    div.innerHTML = '';

    for (const p of parametros) {

        parametro = todos_parametros[algoritmo][p];
        const label = document.createElement('label');
        label.textContent = parametro.label;

        if (parametro.type === 'select') {
            const select = document.createElement('select');
            select.classList.add('form-select');
            select.name = p;

            for (const opcion of parametro.options) {
                const option = document.createElement('option');
                option.value = opcion;
                option.text = opcion;
                select.appendChild(option);
            }
            select.value = parametro.default;
            div.appendChild(label);
            div.appendChild(select);

        }else{
            const input = document.createElement('input');
            input.type = parametro.type;
            input.name = p;
            input.classList.add('form-control');
            input.value = parametro.default;
            div.appendChild(label);
            div.appendChild(input);
        }

    }
    div.appendChild(document.createElement('br'));
}

function validarNumeroEntero(id,min,max) {
    var value = document.getElementById(id).value;
    var entero = parseInt(value)
    if (entero < min || entero > max){
        alert("El número debe estar entre " + min + " y " + max);
        document.getElementById(id).value = "";
    }
}

function validarNumeroFlotante(id,min,max) {
    var value = document.getElementById(id).value;
    var entero = parseFloat(value)
    if (entero < min || entero > max){
        alert("El número debe estar entre " + min + " y " + max);
        document.getElementById(id).value = "";
    }
}

function noetiquetados(checked,id){
    document.getElementById(id).disabled = !!checked;
}