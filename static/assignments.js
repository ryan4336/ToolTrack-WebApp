// Find the search field, status filter, date filters, assignment rows, and messages
const searchInput = document.getElementById("assignment-search");
const statusFilter = document.getElementById("assignment-status");
const dateTypeFilter = document.getElementById("date-type");
const dateFromInput = document.getElementById("date-from");
const dateThroughInput = document.getElementById("date-through");
const dateError = document.getElementById("date-error");
const assignmentRows = document.querySelectorAll(".list-row");
const noResults = document.getElementById("no-assignment-results");
const clearFiltersBtn = document.getElementById("clear-filters");

let searchTimer;

// Apply the search, status, and date filters together
function filterAssignments() {
    const search = searchInput.value.trim().toLowerCase();
    const status = statusFilter.value;
    const dateType = dateTypeFilter.value;
    const dateFrom = dateFromInput.value;
    const dateThrough = dateThroughInput.value;
    
    let visibleCount = 0;
    
    // Display an error message if From is after Through
    const hasDateError = dateFrom && dateThrough && dateFrom > dateThrough;
    dateError.hidden = !hasDateError;

    assignmentRows.forEach(function (row) {
        // Check whether the employee or tool information contains the search
        const assignmentText = row.dataset.search.toLowerCase();
        const matchesSearch = assignmentText.includes(search);

        // All accepts either status, otherwise match the selected status
        const matchesStatus = status === "all" || row.dataset.active === status;

        // Date filtering logic
        let matchesDate = true;
        if (!hasDateError && (dateFrom || dateThrough)) {
            const rowDate = row.getAttribute(`data-${dateType}`);
            
            // Exclude assignments without the selected date when a range is applied
            if (!rowDate) {
                matchesDate = false;
            } else {
                if (dateFrom && rowDate < dateFrom) matchesDate = false;
                if (dateThrough && rowDate > dateThrough) matchesDate = false;
            }
        }

        // Display only rows that pass all valid checks; hide all if there's a date error
        const matches = matchesSearch && matchesStatus && matchesDate && !hasDateError;
        row.hidden = !matches;

        if (matches) {
            visibleCount++;
        }
    });

    // Display the existing no-results message when no assignments match
    if (noResults) {
        // Hide standard empty message if the error message is already taking precedence
        noResults.hidden = visibleCount !== 0 || hasDateError;
    }
}

// Wait 300 ms after typing stops before filtering
searchInput.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterAssignments, 300);
});

// Apply filter changes instantly for dropdowns and date inputs
statusFilter.addEventListener("change", filterAssignments);
dateTypeFilter.addEventListener("change", filterAssignments);
dateFromInput.addEventListener("change", filterAssignments);
dateThroughInput.addEventListener("change", filterAssignments);

// Clear filters functionality for Task 39
if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function() {
        searchInput.value = "";
        statusFilter.value = statusFilter.dataset.defaultStatus || "active";
        dateTypeFilter.value = "date-assigned";
        dateFromInput.value = "";
        dateThroughInput.value = "";
        filterAssignments();
    });
}

// Apply the default status selected in the HTML
filterAssignments();