document.getElementById("config_btn").disabled = true;

['dragleave', 'drop', 'dragenter', 'dragover'].forEach(function (evento) {
    document.addEventListener(evento, function (e) {
        e.preventDefault();
    }, false);
});

let area = document.getElementById('soltar');
let progreso = document.getElementById('progreso');

area.addEventListener('drop',soltado,false)

function soltado(e){
    e.preventDefault();
    let archivo = e.dataTransfer.files;

    if (archivo.length >= 2) {
        return false;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('post', '/subida', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("config_btn").disabled = false;
        }
    };

    xhr.upload.onprogress = function (evento) {
        if (evento.lengthComputable) {
            let percent = Math.floor(evento.loaded / evento.total * 100);
            progreso.value = percent;
        }
    };

    let parametros = new FormData();
    parametros.append('archivo',archivo[0])
    xhr.send(parametros);
}
