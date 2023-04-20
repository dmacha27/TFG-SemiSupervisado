// https://datatables.net/forums/discussion/54495/remove-table-row-from-a-button-inside-the-same-row-when-collapsed
// Transformado a vanilla
document.addEventListener('DOMContentLoaded', function() {
  let datasettable = document.querySelector('#datasettable');
  let table = new DataTable(datasettable, {
    responsive: true
  });

  datasettable.addEventListener('click', function(event) {
    if (event.target.classList.contains('remove')) {
      let row = event.target.closest('tr');
      table.row(row).remove().draw();
    }
  });
});