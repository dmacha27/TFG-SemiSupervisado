// https://datatables.net/forums/discussion/54495/remove-table-row-from-a-button-inside-the-same-row-when-collapsed
// Transformado a vanilla
document.addEventListener('DOMContentLoaded', function() {
  let datasettable = document.querySelector('#datasettable');

  let id = document.querySelector('#user_id').value
  let datasets;
  fetch('/datasets/'+id)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)){
          datasets = [];
          for (let dataset of data) {
            datasets.push(JSON.parse(dataset));
          }
        } else {
          datasets = JSON.parse(data);
        }
      })
      .then(() => {
        let table = new DataTable(datasettable, {
          data: datasets
        });
      });

  datasettable.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove')) {
      let row = event.target.closest('tr');
      table.row(row).remove().draw();
    }
  });
});