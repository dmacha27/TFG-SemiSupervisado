document.getElementById("config_btn").disabled = true;

['dragleave', 'drop', 'dragenter', 'dragover'].forEach(function (evento) {
    document.addEventListener(evento, function (e) {
        e.preventDefault();
    }, false);
});

let area = document.getElementById('soltar');
area.param = 'soltar'
let progreso = document.getElementById('progreso');

let boton = document.getElementById('archivo');
boton.param = 'boton'

area.addEventListener('drop',subir,false)
boton.addEventListener('change',subir)


/**
 *
 * Gestiona la subida del fichero realizando una petición post
 * sobre una ruta de la aplicación.
 * Gracias al evento del proceso permite determinar el porcentaje de subida.
 *
 * @param e - evento
 * @returns {boolean} - false si existe algún problema
 */
function subir(e){
    e.preventDefault();
    let archivo;

    if (e.currentTarget.param === 'soltar') {
        archivo = e.dataTransfer.files; // arrastar y soltar
    }else{
        archivo = e.target.files; // botón de subida
    }
    if (archivo.length >= 2) {
        return false;
    }

    let xhr = new XMLHttpRequest();
    xhr.open('post', '/subida', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("config_btn").disabled = false;
        }
    };

    xhr.upload.onprogress = function (evento) {
        if (evento.lengthComputable) {
            progreso.value = Math.floor(evento.loaded / evento.total * 100);
        }
    };

    let params= new FormData();
    params.append('archivo',archivo[0])
    xhr.send(params);
}
