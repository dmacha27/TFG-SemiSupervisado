// https://datatables.net/forums/discussion/54495/remove-table-row-from-a-button-inside-the-same-row-when-collapsed
// Transformado a vanilla
function nombredataset(file) {
    return file.split("-")[0];
}

document.addEventListener('DOMContentLoaded', function() {

    let id = document.querySelector('#user_id').value

    { // TABLA DE DATASETS
        let datasettable = document.querySelector('#datasettable');

        let datasets;
        let table;

        fetch('/datasets/obtener/' + id)
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    datasets = [];
                    for (let dataset of data) {
                        //["file","date"]
                        let aux = JSON.parse(dataset);

                        datasets.push([nombredataset(aux[0]), aux[0], aux[1], ""]);
                    }
                } else {
                    let aux = JSON.parse(data);
                    datasets = [[nombredataset(aux[0]), aux[0], aux[1], ""]];
                }
            })
            .then(() => {
                table = new DataTable(datasettable, {
                    "order": [[2, 'desc']],
                    "responsive": true,
                    "pageLength": 5,
                    "lengthMenu": [[5, 10, 20], [5, 10, 20]],
                    "data": datasets,
                    "columnDefs": [
                        {"className": "align-middle", "targets": "_all"},
                        {
                            "targets": -1,
                            "className": "dt-body-center",
                            "orderable": false,
                            "render": function (data, type, row, meta) {
                                return '<button type="button" class="btn btn-warning run" data-file="' + row[1] + '">' +
                                    '<div class="pe-none">' +
                                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-play-fill" viewBox="0 0 16 16">\n' +
                                    '  <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>\n' +
                                    '</svg>' +
                                    '</div>' +
                                    '</button> ' +
                                    '<button class="btn btn-danger remove" data-file="' + row[1] + '"><div class="pe-none">' +
                                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-trash-fill" viewBox="0 0 16 16">\n' +
                                    '  <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>\n' +
                                    '</svg></div></button>';
                            }
                        }, {
                            target: 1,
                            visible: false,
                            searchable: false,
                        }]
                });
            });

        datasettable.addEventListener('click', function (event) {
            // Eliminar
            if (event.target.classList.contains('remove')) {
                let file = event.target.getAttribute('data-file');

                let span_fichero = document.getElementById('nombre_fichero_modal');
                span_fichero.innerHTML = nombredataset(file);

                let modal = new bootstrap.Modal(document.getElementById('modal_eliminar'));
                modal.show();

                let btn_eliminar = document.getElementById('btn_eliminar');
                btn_eliminar.onclick = function (e) {
                    modal.hide();
                    fetch('/datasets/eliminar', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            "fichero": file,
                            "id": id
                        })
                    }).then(res => res.json())
                        .catch(error => console.log(error));
                    let row = event.target.closest('tr');
                    table.row(row).remove().draw();

                    let n_uploads = document.getElementById('n_uploads');
                    n_uploads.innerHTML = (parseInt(n_uploads.innerHTML) - 1).toString();

                }
                // Ejecutar
            } else if (event.target.classList.contains('run')) {
                let file = event.target.getAttribute('data-file');

                let modal = new bootstrap.Modal(document.getElementById('modal_ejecutar'));
                modal.show();

                let selftraining = document.getElementById('selftraining_link');
                selftraining.setAttribute('href', '/seleccionar/selftraining/' + file);

                let cotraining = document.getElementById('cotraining_link');
                cotraining.setAttribute('href', '/seleccionar/cotraining/' + file);

                let democraticcolearning = document.getElementById('democraticcolearning_link');
                democraticcolearning.setAttribute('href', '/seleccionar/democraticcolearning/' + file);

                let triraining = document.getElementById('triraining_link');
                triraining.setAttribute('href', '/seleccionar/triraining/' + file);

            }
        });
    }


    { // TABLA DE HISTORIAL DE EJECUCIÓN
        let titulos = {'selftraining': 'Self-Training',
            'cotraining': 'Co-Training',
            'democraticcolearning': 'Democratic Co-Learning',
            'tritraining': 'Tri-Training'};

        let historytable = document.querySelector('#historytable');

        let historial;
        let table;

        fetch('/historial/obtener/' + id)
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    historial = [];
                    for (let dataset of data) {
                        //["id", "algorithm","filename","date","cx", "cy", "jsonfile"]
                        let aux = JSON.parse(dataset);

                        historial.push([aux[1], nombredataset(aux[2]), aux[3], aux[0], aux[4], aux[5], aux[6]]);
                    }
                } else {
                    let aux = JSON.parse(data);
                    historial = [[aux[1], nombredataset(aux[2]), aux[3], aux[0], aux[4], aux[5], aux[6]]];
                }
            })
            .then(() => {
                new DataTable(historytable, {
                    "order": [[2, 'desc']],
                    "responsive": true,
                    "pageLength": 5,
                    "lengthMenu": [[5, 10, 20], [5, 10, 20]],
                    "data": historial,
                    "columnDefs": [
                        {"className": "align-middle", "targets": "_all"},
                        {
                            "targets": 0,
                            "render": function (data, type, row, meta) {
                                return titulos[row[0]]; // Sustituir nombre del algoritmo por su título
                            }
                        },
                        {
                            "targets": -1,
                            "className": "dt-body-center",
                            "orderable": false,
                            "render": function (data, type, row, meta) {
                                return '<a type="button" class="btn btn-warning run" href="/visualizacion/' + row[0] +'/' + row[3] +'">' +
                                    '<div class="pe-none">' +
                                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-play-fill" viewBox="0 0 16 16">\n<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-arrow-clockwise" viewBox="0 0 16 16">\n' +
                                    '  <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>\n' +
                                    '  <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>\n' +
                                    '</svg>' +
                                    '</div>' +
                                    '</a>';
                            }
                        }]
                });
            });
    }
});