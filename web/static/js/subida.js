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

function subir(e){
    e.preventDefault();
    let archivo;

    if (e.currentTarget.param === 'soltar') {
        archivo = e.dataTransfer.files;
    }else{
        archivo = e.target.files;
    }
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
            progreso.value = Math.floor(evento.loaded / evento.total * 100);
        }
    };

    let parametros = new FormData();
    parametros.append('archivo',archivo[0])
    xhr.send(parametros);
}
