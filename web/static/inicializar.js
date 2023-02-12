let datos;
let cont = 0;

async function inicializar(rutadatos, elementos) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE) {
                datos = JSON.parse(xhr.responseText);
                document.getElementById("div_cargando").remove();
                document.getElementById("controles").style.visibility = 'visible';

                resolve("RECIBIDO");
            }
        }

        xhr.open("POST", rutadatos);
        let parametros = new FormData();
        elementos.forEach(el => {
            parametros.append(el.nombre, el.valor)
        });
        xhr.send(parametros);
    });
}