// https://datatables.net/forums/discussion/54495/remove-table-row-from-a-button-inside-the-same-row-when-collapsed
// Transformado a vanilla
function nombredataset(file) {
    return file.split("-")[0];
}

document.addEventListener('DOMContentLoaded', function() {
    let datasettable = document.querySelector('#datasettable');

    let id = document.querySelector('#user_id').value
    let datasets;
    let table;

    function eliminar(boton) {
        console.log(boton)
    }

    const funcion_eliminar = eliminar;

    fetch('/datasets/obtener/'+id)
        .then(res => res.json())
        .then(data => {
            if (Array.isArray(data)){
                datasets = [];
                for (let dataset of data) {
                    //["file","date"]
                    let aux = JSON.parse(dataset);

                    datasets.push([nombredataset(aux[0]), aux[0], aux[1]]);
                }
            } else {
                let aux = JSON.parse(data);
                datasets = [[nombredataset(aux[0]), aux[0], aux[1]]];
            }
        })
        .then(() => {
            table = new DataTable(datasettable, {
                "order": [[2, 'desc']],
                "responsive": true,
                "pageLength" : 5,
                "lengthMenu": [[5, 10, 20], [5, 10, 20]],
                "data": datasets,
                "columnDefs": [
                    {"className": "align-middle", "targets": "_all"},
                    {
                        "targets": -1,
                        "render": function ( data, type, row, meta )
                        {
                            return '<button type="button" class="btn btn-warning" data-bs-toggle="modal" data-bs-target="#miespacio_modal">' +
                                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-play-fill" viewBox="0 0 16 16">\n' +
                                '  <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>\n' +
                                '</svg></button> ' +
                                '<button class="btn btn-danger remove" data-file="'+row[1]+'"><div class="pe-none">' +
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



    datasettable.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove')) {
            let file = event.target.getAttribute('data-file');

            let modal = new bootstrap.Modal(document.getElementById('miespacio_modal'));
            modal.show();
            fetch('/datasets/eliminar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(file)
            }).then(res => res.json())
            let row = event.target.closest('tr');
            table.row(row).remove().draw();
        }
    });
});