import {generateDatasetList, generateRunList, generateDatasetTable, generateHistoryTable} from './funciones_tablas.js';

document.addEventListener('DOMContentLoaded', function() {

    generateDatasetList()
        .then(datasets => {
            generateDatasetTable(datasets, true);
        })

    generateRunList()
        .then(historial => {
            generateHistoryTable(historial, true);
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