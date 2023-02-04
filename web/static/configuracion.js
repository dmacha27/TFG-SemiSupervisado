
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

function noetiquetados(checked,id){
    document.getElementById(id).disabled = !!checked;
}