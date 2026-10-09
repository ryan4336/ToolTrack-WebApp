// search bar will search all fields (minus status and Admin) for any matching strings anywhere within those fields. 
// Search will happen on user input, but delay 300ms and reset on input so the browser is not acting on every single typed letter

// Find the search field, employee rows, and empty-results message
const searchInput = document.getElementById("employee-search");
const employeeRows = document.querySelectorAll(".employee-row");
const noResults = document.getElementById("no-search-results");

//Search should happen after 300 milliseconds of no typing to reduce load on browser

// make a timer so it can be reset when the user keeps typing
let searchTimer;

// Function that runs whenever the user types or clears the search field
searchInput.addEventListener("input", function () {
    // Reset the search timer since an action was performed
    clearTimeout(searchTimer);

    // Use setTimeout to set 300 ms as timeout, and function to run after timeout
    searchTimer = setTimeout(function () {
        const search = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        employeeRows.forEach(function (row) {
            // Search the employee's ID, name, email, phone, and job title
            const employeeText = row.dataset.search.toLowerCase();
            let matches = employeeText.includes(search);

            // Hide rows that don't match
            row.hidden = !matches;

            if (matches) {
                visibleCount++;
            }
        });

        // Display the message when no employees match the search
        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }
    }, 300);
});
