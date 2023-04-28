import {
    generateDatasetList,
    generateRunList,
    generateDatasetTable,
    generateHistoryTable,
    generateUserList,
    generateUserTable
} from './funciones_tablas.js';

document.addEventListener('DOMContentLoaded', function() {

    generateDatasetList()
        .then(datasets => {
            generateDatasetTable(datasets, true);
        })

    generateRunList()
        .then(historial => {
            generateHistoryTable(historial, true);
        })

    generateUserList()
        .then(users => {
            let total_users = document.getElementById('total_users');
            total_users.innerText = users.length.toString();
            generateUserTable(users);
        })

    fetch('/datasets/ultimos')
            .then(res => res.json())
            .then(data => {
                let recent_uploads = document.getElementById('recent_datasets');
                recent_uploads.innerText = data;
            });


    fetch('/historial/ultimos')
            .then(res => res.json())
            .then(data => {
                let recent_runs = document.getElementById('recent_runs');
                recent_runs.innerText = data;
            });
});