let cont = 0;

async function inicializar(rutadatos, elementos) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE) {
                let datos = JSON.parse(xhr.responseText);
                document.getElementById("div_cargando").remove();
                document.getElementById("visualizacion").style.visibility = 'visible';

                resolve(datos);
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

function panelInfo(){
    let card_info = document.getElementById("card_info")
    let card_info_text = document.getElementById("card_info_text")

    if (card_info.style.width === "400px"){
        card_info.style.width = "0px";
        card_info_text.style.display = "none";
    }else{
        card_info.style.width = "400px";
        card_info_text.style.display = "block";
    }
}