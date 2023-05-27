document.addEventListener('DOMContentLoaded', function() {
    ['dragleave', 'drop', 'dragenter', 'dragover'].forEach(function (evento) {
        document.addEventListener(evento, function (e) {
            e.preventDefault();
        }, false);
    });

    let area = document.getElementById('soltar');
    area.param = 'soltar';

    let progreso = document.getElementById('progreso');
    let porcentaje_progreso = document.getElementById('porcentaje_progreso');
    let nombre_fichero = document.getElementById('nombre_fichero');

    let boton = document.getElementById('archivo');
    boton.param = 'boton';

    area.addEventListener('drop', subir, false)
    boton.addEventListener('change', subir)


    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    let btn_condiciones = document.getElementById('btn_condiciones');
    btn_condiciones.onclick = function (e) {
        let modal = new bootstrap.Modal(document.getElementById('modal_condiciones'));
        modal.show();
    }

    /**
     *
     * Gestiona la subida del fichero realizando una petición post
     * sobre una ruta de la aplicación.
     * Gracias al evento del proceso permite determinar el porcentaje de subida.
     *
     * @param e - evento
     * @returns {boolean} - false si existe algún problema
     */
    function subir(e) {
        e.preventDefault();
        let archivo;

        if (e.currentTarget.param === 'soltar') {
            archivo = e.dataTransfer.files; // arrastar y soltar
        } else {
            archivo = e.target.files; // botón de subida
        }
        if (archivo.length >= 2) {
            return false;
        }

        nombre_fichero.textContent = archivo[0].name;

        let xhr = new XMLHttpRequest();
        xhr.open('post', '/subida', true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                let button = document.querySelector("#fichero-previo");
                if (button == null) {
                    document.getElementById("config_btn").disabled = false;
                } else {
                    button.style.display = "none";
                }
            }
        };

        xhr.upload.onprogress = function (evento) {
            if (evento.lengthComputable) {
                let porcentaje = Math.floor(evento.loaded / evento.total * 100);
                progreso.style.width = porcentaje.toString() + "%";
                progreso.setAttribute("aria-valuenow", porcentaje.toString());
                porcentaje_progreso.textContent = porcentaje.toString() + "%";
            }
        };

        xhr.setRequestHeader('X-CSRFToken', document.querySelector('meta[name="csrf-token"]').getAttribute('content'));
        let params = new FormData();
        params.append('archivo', archivo[0])
        xhr.send(params);
    }
});
