import {generateDatasetList, generateRunList, generateDatasetTable, generateHistoryTable} from './funciones_tablas.js';

document.addEventListener('DOMContentLoaded', function() {

    let id = document.querySelector('#user_id').value;

    generateDatasetList(id)
        .then(datasets => {
            generateDatasetTable(datasets, locale,false);
        })

    generateRunList(id)
        .then(historial => {
            generateHistoryTable(historial, locale,false);
        })

});