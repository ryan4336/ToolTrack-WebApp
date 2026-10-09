// search bar will search all fields (minus status and Admin) for any matching strings anywhere within those fields. 
// Search will happen on user input, but delay 300ms and reset on input so the browser is not acting on every single typed letter

// Find the search field, employee rows, empty-results message, and status filter
const searchInput = document.getElementById("employee-search");
const employeeRows = document.querySelectorAll(".employee-row");
const noResults = document.getElementById("no-search-results");
const statusFilter = document.getElementById("employee-status");

let searchTimer;

// Apply both the text search and the selected employment status
function filterEmployees() {
    const search = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;
    let visibleCount = 0;

    employeeRows.forEach(function (row) {
        const employeeText = row.dataset.search.toLowerCase();
        const matchesSearch = employeeText.includes(search);

        // 'All' should accept either status
        const matchesStatus =
            status === "all" || row.dataset.active === status;

        // Only display employees that match both searches
        const matches = matchesSearch && matchesStatus;
        row.hidden = !matches;

        if (matches) {
            visibleCount++;
        }
    });
     
    if (noResults) {
        noResults.hidden = visibleCount !== 0;
    }
}

// Wait 300 milliseconds after typing stops before filtering
searchInput.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterEmployees, 300);
});

// Apply status changes immediately
statusFilter.addEventListener("change", function () {
    clearTimeout(searchTimer);
    filterEmployees();
});

// Apply the default Active filter when the page loads
filterEmployees();


