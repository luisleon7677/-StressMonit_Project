/**
 * Filtro de búsqueda para tablas con paginación.
 * Uso: initTableSearch('tablaId', { rowSelector: 'tr.fila-principal', hasDetailsRow: true, onFilter: () => paginarTabla() })
 */
function initTableSearch(tableId, options = {}) {
  const { rowSelector = 'tr', hasDetailsRow = false, onFilter } = options;
  const input = document.querySelector(`.input-busqueda-tabla[data-tabla-id="${tableId}"]`);
  const tbody = document.getElementById('tablaBody');
  if (!input || !tbody) return () => [];

  function getFilteredRows() {
    const term = (input.value || '').trim().toLowerCase();
    const allRows = Array.from(tbody.querySelectorAll(rowSelector));
    if (!term) {
      allRows.forEach(r => r.classList.remove('search-no-match'));
      if (hasDetailsRow) {
        tbody.querySelectorAll('.details-row').forEach(d => d.classList.remove('search-no-match'));
      }
      return allRows;
    }
    allRows.forEach(row => {
      const text = row.textContent || '';
      const match = text.toLowerCase().includes(term);
      row.classList.toggle('search-no-match', !match);
      if (hasDetailsRow) {
        const details = row.nextElementSibling;
        if (details && details.classList.contains('details-row')) {
          details.classList.toggle('search-no-match', !match);
        }
      }
    });
    return allRows.filter(r => !r.classList.contains('search-no-match'));
  }

  input.addEventListener('input', () => {
    getFilteredRows();
    onFilter && onFilter();
  });

  return getFilteredRows;
}
