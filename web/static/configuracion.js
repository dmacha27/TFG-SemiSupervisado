
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