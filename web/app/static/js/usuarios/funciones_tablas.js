function nombredataset(file) {
    return file.split("-")[0];
}

const idiomas = {
    "en": {
        "decimal":        "",
        "emptyTable":     "No data available in table",
        "info":           "Showing _START_ to _END_ of _TOTAL_ entries",
        "infoEmpty":      "Showing 0 to 0 of 0 entries",
        "infoFiltered":   "(filtered from _MAX_ total entries)",
        "infoPostFix":    "",
        "thousands":      ",",
        "lengthMenu":     "Show _MENU_ entries",
        "loadingRecords": "Loading...",
        "processing":     "",
        "search":         "Search:",
        "zeroRecords":    "No matching records found",
        "paginate": {
            "first":      "First",
            "last":       "Last",
            "next":       "Next",
            "previous":   "Previous"
        }
    },
    "es": {
        "decimal": "",
        "emptyTable": "No hay información",
        "info": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
        "infoEmpty": "Mostrando 0 to 0 of 0 entradas",
        "infoFiltered": "(Filtrado de _MAX_ total entradas)",
        "infoPostFix": "",
        "thousands": ",",
        "lengthMenu": "Mostrar _MENU_ entradas",
        "loadingRecords": "Cargando...",
        "processing": "Procesando...",
        "search": "Buscar:",
        "zeroRecords": "No hay datos en la tabla",
        "paginate": {
            "first": "Primero",
            "last": "Último",
            "next": "Siguiente",
            "previous": "Anterior"
        }
    }
}

const titulos = {'selftraining': 'Self-Training',
    'cotraining': 'Co-Training',
    'democraticcolearning': 'Democratic Co-Learning',
    'tritraining': 'Tri-Training'};

export const generateDatasetList = async (id=null) => {
    id = id==null ? '' : '/' + id;
    let response = await fetch('/datasets/obtener' + id);
    let data = await response.json();

    let datasets;

    if (Array.isArray(data)) {
        datasets = [];
        for (let dataset of data) {
            //["file","date", "user"]
            let aux = JSON.parse(dataset);

            datasets.push([nombredataset(aux[0]), aux[0], aux[1], aux[2], ""]);
        }
    } else {
        let aux = JSON.parse(data);
        datasets = [[nombredataset(aux[0]), aux[0], aux[1], aux[2], ""]];
    }
    return datasets;
}

export const generateRunList = async (id=null) => {
    id = id==null ? '' : '/' + id;
    let response = await fetch('/historial/obtener' + id)
    let data = await response.json();

    let historial;
    if (Array.isArray(data)) {
        historial = [];
        for (let run of data) {
            //["id", "algorithm","filename","date","user", "cx", "cy", "jsonfile", "json_parameters"]
            let aux = JSON.parse(run);
            //Añadir una columna usuario en el <table>                             | //OCULTO
            historial.push([aux[1], nombredataset(aux[2]), aux[3], aux[8], aux[4], aux[0], aux[5], aux[6], aux[7]]);
        }
    } else {
        let aux = JSON.parse(data);
        historial = [[aux[1], nombredataset(aux[2]), aux[3], aux[8], aux[4], aux[0], aux[5], aux[6], aux[7]]];
    }

    return historial;
}

export const generateUserList = async () => {
    let response = await fetch('/usuarios/obtener');
    let data = await response.json();

    let usuarios;

    if (Array.isArray(data)) {
        usuarios = [];
        for (let usuario of data) {
            //["id","name","email","last_login"]
            let aux = JSON.parse(usuario);

            usuarios.push([aux[1], aux[2], aux[3], aux[0]]);
        }
    } else {
        let aux = JSON.parse(data);
        usuarios = [[aux[1], aux[2], aux[3], aux[0]]];
    }
    return usuarios;
}

function fetch_eliminar(ruta, table, row, file, id) {
    fetch(ruta, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({
            "fichero": file,
            "id": id
        })
    }).then(function (response) {
        if (!response.ok){
            let error_modal = new bootstrap.Modal(document.getElementById('modal_error'));
            error_modal.show();
        } else {
            table.row(row).remove().draw();
        }
    })
        .catch(error => console.log(error));
}


// https://datatables.net/forums/discussion/54495/remove-table-row-from-a-button-inside-the-same-row-when-collapsed
// Transformado a vanilla
export function generateDatasetTable(datasets, locale, all_users) {

    let datasettable = document.querySelector('#datasettable');

    let table = new DataTable(datasettable, {
        "order": [[2, 'desc']],
        "responsive": true,
        "pageLength": 5,
        "language": idiomas[locale],
        "lengthMenu": [[5, 10, 20], [5, 10, 20]],
        "data": datasets,
        "columnDefs": [
            {"className": "align-middle", "targets": "_all"},
            {
                "targets": -1, // Columna acciones
                "className": "dt-body-center",
                "orderable": false,
                "render": function (data, type, row, meta) {

                    let acciones = '';
                    if (!all_users) {
                        acciones += '<button type="button" class="btn btn-warning run" data-file="' + row[1] + '">' +
                            '<div class="pe-none">' +
                            '<i class="bi bi-play-fill text-white"></i>' +
                            '</div>' +
                            '</button>'
                    }
                    acciones += '    <button class="btn btn-danger remove" data-file="' + row[1] + '">' +
                        '<div class="pe-none">' +
                        '<i class="bi bi-trash-fill text-white"></i>' +
                        '</div>' +
                        '</button>'

                    return acciones;
                }
            }, {
                "target": 1,
                "visible": false,
                "searchable": false,
            }, {
                "targets": -2, // Columna user
                "visible": all_users, // Si la tabla es para todos los datasets de todos los usuarios, esta columna será visible
                "searchable": all_users,
            }]
    });

    let id;

    if (all_users) {
        id = -1;
    } else {
        id = document.querySelector('#user_id').value;
    }

    datasettable.addEventListener('click', function (event) {
        // Eliminar
        if (event.target.classList.contains('remove')) {
            let file = event.target.getAttribute('data-file');

            let row = event.target.closest('tr');

            let span_fichero = document.getElementById('nombre_fichero_modal');
            span_fichero.innerHTML = nombredataset(file);

            if (all_users) {
                span_fichero.innerHTML += ' (' + row.cells[2].innerText + ')'
            }

            let modal = new bootstrap.Modal(document.getElementById('modal_eliminar'));
            modal.show();

            let btn_eliminar = document.getElementById('btn_eliminar');
            btn_eliminar.onclick = function (e) {
                modal.hide()
                fetch_eliminar('/datasets/eliminar', table, row, file, id);
                if (!all_users) {
                    let n_uploads = document.getElementById('n_uploads');
                    n_uploads.innerHTML = (parseInt(n_uploads.innerHTML) - 1).toString();
                }

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

export function generateHistoryTable(historial, locale, all_users) {

    let historytable = document.querySelector('#historytable');

    let table = new DataTable(historytable, {
        "order": [[2, 'desc']],
        "responsive": true,
        "pageLength": 5,
        "language": idiomas[locale],
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
                "targets": 3, // Columna acciones
                "className": "dt-body-center",
                "orderable": false,
                "render": function (data, type, row, meta) {
                    return '<button class="btn btn-success parameters">' +
                        '<div class="pe-none">' +
                        '<i class="bi bi-file-earmark-spreadsheet-fill"></i>' +
                        '</div>' +
                        '</button>';
                }
            },
            {
                "targets": -1, // Columna acciones
                "className": "dt-body-center",
                "orderable": false,
                "render": function (data, type, row, meta) {
                    console.log(row)
                    let acciones = '';
                    if (!all_users) {
                        acciones += '<a type="button" class="btn btn-warning run" href="/visualizacion/' + row[0] +'/' + row[5] +'">' +
                            '<div class="pe-none">' +
                            '<i class="bi bi-arrow-clockwise text-white"></i>' +
                            '</div>' +
                            '</a>'
                    }
                    acciones += '    <button class="btn btn-danger remove" data-file="' + row[8] + '">' +
                        '<div class="pe-none">' +
                        '<i class="bi bi-trash-fill text-white"></i>' +
                        '</div>' +
                        '</button>'

                    return acciones;
                }
            }, {
                "targets": -2, // Columna user
                "visible": all_users, // Si la tabla es para todos los datasets de todos los usuarios, esta columna será visible
                "searchable": all_users,
            }]
    });

    let id;

    if (all_users) {
        id = -1;
    } else {
        id = document.querySelector('#user_id').value;
    }

    historytable.addEventListener('click', function (event) {
        // Eliminar
        if (event.target.classList.contains('remove')) {
            let file = event.target.getAttribute('data-file');

            let row = event.target.closest('tr');

            let span_fichero = document.getElementById('nombre_fichero_modal');
            span_fichero.innerHTML = row.cells[0].innerText + ' - ' + row.cells[1].innerText + ' (' + row.cells[2].innerText + ')';

            let modal = new bootstrap.Modal(document.getElementById('modal_eliminar'));
            modal.show();

            let btn_eliminar = document.getElementById('btn_eliminar');
            btn_eliminar.onclick = function (e) {
                modal.hide();
                fetch_eliminar('/historial/eliminar', table, row, file, id);
            }
        } else if (event.target.classList.contains('parameters')){
            let row = event.target.closest('tr');
            let json = JSON.parse(table.row(row).data()[3])

            let modal = new bootstrap.Modal(document.getElementById('modal_parametros'));
            modal.show();

            document.getElementById("json_parameters").innerHTML = JSON.stringify(json, null, "  ");

        }
    });
}

export function generateUserTable(usuarios, locale) {

    let usertable = document.querySelector('#usertable');

    let table = new DataTable(usertable, {
        "order": [[2, 'desc']],
        "responsive": true,
        "pageLength": 5,
        "language": idiomas[locale],
        "lengthMenu": [[5, 10, 20], [5, 10, 20]],
        "data": usuarios,
        "columnDefs": [
            {"className": "align-middle", "targets": "_all"},
            {
                "targets": -1, // Columna acciones
                "className": "dt-body-center",
                "orderable": false,
                "render": function (data, type, row, meta) {
                    return '<a type="button" class="btn btn-success edit" href="/admin/usuario/editar/' + row[3] + '">' +
                        '<div class="pe-none">' +
                        '<i class="bi bi-pencil-fill text-white"></i>' +
                        '</div>' +
                        '<a>'
                        +'  <button class="btn btn-danger remove" data-user="' + row[3] + '">' +
                        '<div class="pe-none">' +
                        '<i class="bi bi-trash-fill text-white"></i>' +
                        '</div>' +
                        '</button>';
                }
            }]
    });

    usertable.addEventListener('click', function (event) {
        // Eliminar
        if (event.target.classList.contains('remove')) {
            let user = event.target.getAttribute('data-user');

            let row = event.target.closest('tr');

            let span_usuario = document.getElementById('nombre_fichero_modal');
            span_usuario.innerText = row.cells[0].innerText + ' (' + row.cells[1].innerText + ')' ;

            let modal = new bootstrap.Modal(document.getElementById('modal_eliminar'));
            modal.show();

            let btn_eliminar = document.getElementById('btn_eliminar');
            btn_eliminar.onclick = function (e) {
                modal.hide();
                fetch('/usuarios/eliminar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "user_id": user
                    })
                }).then(function (response) {
                    if (!response.ok){
                        let error_modal = new bootstrap.Modal(document.getElementById('modal_error'));
                        error_modal.show();
                    } else {
                        table.row(row).remove().draw();
                        location.reload();
                    }
                })
                    .catch(error => console.log(error));

            }
        }
    });
}
