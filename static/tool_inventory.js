
const searchInput = document.getElementById("tool-search");
const toolRows = document.querySelectorAll(".tool-row");
const noResults = document.getElementById("no-search-results");
const statusFilter = document.getElementById("tool-status");
const conditionFilter = document.getElementById("tool-condition");

let searchTimer;

function filterTools() {
    const search = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;
    const condition = conditionFilter.value;
    let visibleCount = 0;

    toolRows.forEach(function (row) {
        const toolText = row.dataset.search.toLowerCase();
        const matchesSearch = toolText.includes(search);

        const matchesStatus = status === "all" || row.dataset.status === status;
        const matchesCondition = status === "all" || row.dataset.condtion === condition;
        const matches = matchesSearch && matchesStatus && matchesCondition;
        row.hidden = !matches;

        if (matches) {
            visibleCount++
        }
    });

    if(noResults) {
        noResults.hidden = visibleCount !== 0;
    }
}

// Wait 300 milliseconds after typing stops before filtering
searchInput.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterTools, 300);
});

// Apply status and condition changes immediately
statusFilter.addEventListener("change", function () {
    clearTimeout(searchTimer);
    filterTools();
});

conditionFilter.addEventListener("change", function () {
    clearTimeout(searchTimer);
    filterTools();
});

filterTools();