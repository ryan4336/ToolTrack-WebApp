const searchInput = document.getElementById("category-search");
const categoryRows = document.querySelectorAll(".list-row");
const noResults = document.getElementById("no-search-results");

let searchTimer;

function filterCategories() {
    const search = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    categoryRows.forEach(function (row) {
        const categoryText = row.dataset.search.toLowerCase();
        const matchesSearch = categoryText.includes(search);
        
        row.hidden = !matchesSearch;

        if (matchesSearch) {
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
    searchTimer = setTimeout(filterCategories, 300);
});

// Run initial filter on page load
filterCategories();