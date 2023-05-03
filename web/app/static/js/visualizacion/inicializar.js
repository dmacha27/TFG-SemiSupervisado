let cont = 0;

/**
 *
 * Se encarga de inicializar la visualización de forma asíncrona
 * (para que la Web prosiga sin necesidad de esperar a finalizar esta funcion).
 * La idea es realizar una petición POST sobre una ruta preparada en la que se ejecuta
 * el algoritmo. Obtiene los datos y los convierte a JSON.
 *
 * @param rutadatos - ruta (endpoint) para la petición
 * @param elementos - los elementos/parámetros de los algoritmos
 * @returns {Promise<unknown>}
 */
async function inicializar(rutadatos, elementos) {
    return new Promise((resolve) => {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE) {
                let datos = JSON.parse(xhr.responseText);
                document.getElementById("div_cargando").remove();
                document.getElementById("visualizacion").style.visibility = 'visible';
                document.getElementById("titulo_visualizacion").style.visibility = 'visible';

                resolve(datos);
            }
        }

        xhr.open("POST", rutadatos);
        xhr.setRequestHeader('X-CSRFToken', document.querySelector('meta[name="csrf-token"]').getAttribute('content'));
        let parametros = new FormData();
        elementos.forEach(el => {
            parametros.append(el.nombre, el.valor)
        });
        xhr.send(parametros);
    });
}
