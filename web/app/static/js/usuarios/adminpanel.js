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
            generateDatasetTable(datasets, locale,true);
        })
        .catch(error => {console.log(error)});

    generateRunList()
        .then(historial => {
            generateHistoryTable(historial, locale, true);
        })
        .catch(error => {console.log(error)});

    generateUserList()
        .then(users => {
            let total_users = document.getElementById('total_users');
            total_users.innerText = users.length.toString();
            generateUserTable(users, locale);
        })
        .catch(error => {console.log(error)});

    fetch('/datasets/ultimos')
        .then(res => res.json())
        .then(data => {
            let recent_uploads = document.getElementById('recent_datasets');
            recent_uploads.innerText = data;
        })
        .catch(error => {console.log(error)});


    fetch('/historial/ultimos')
        .then(res => res.json())
        .then(data => {
            let recent_runs = document.getElementById('recent_runs');
            recent_runs.innerText = data;
        })
        .catch(error => {console.log(error)});
});