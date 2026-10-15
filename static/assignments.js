// Find the search field, status filter, assignment rows, and message
const searchInput = document.getElementById("assignment-search");
const statusFilter = document.getElementById("assignment-status");
const assignmentRows = document.querySelectorAll(".list-row");
const noResults = document.getElementById("no-assignment-results");

let searchTimer;

// Apply the search and status filter together
function filterAssignments() {
    const search = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;
    let visibleCount = 0;

    assignmentRows.forEach(function (row) {
        // Check whether the employee or tool information contains the search
        const assignmentText = row.dataset.search.toLowerCase();
        const matchesSearch = assignmentText.includes(search);

        // All accepts either status, otherwise match the selected status
        const matchesStatus =
            status === "all" || row.dataset.active === status;

        // Display only rows that pass both checks
        const matches = matchesSearch && matchesStatus;
        row.hidden = !matches;

        if (matches) {
            visibleCount++;
        }
    });

    // This message exists only when assignments were loaded
    if (noResults) {
        noResults.hidden = visibleCount !== 0;
    }
}

// Wait 300 ms after typing stops before filtering
searchInput.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterAssignments, 300);
});

// Apply status changes 
statusFilter.addEventListener("change", function () {
    clearTimeout(searchTimer);
    filterAssignments();
});

// Apply the default Active filter when the page opens
filterAssignments();