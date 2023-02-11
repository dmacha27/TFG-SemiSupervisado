let datos, dataset = [];
let cont = 0;

function inicializar(rutadatos, elementos) {

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE) {
            datos = JSON.parse(xhr.responseText);
            document.getElementById("div_cargando").remove();

            document.getElementById("controles").style.visibility = 'visible';

            //Se inicializa el gráfico
            inicializarGrafico(preparardataset,databinding)

            //Se inicializan las estadísticas
        }
    }

    xhr.open("POST", rutadatos);
    let parametros = new FormData();
    elementos.forEach(el => {
        parametros.append(el.nombre,el.valor)
    });
    xhr.send(parametros);
}