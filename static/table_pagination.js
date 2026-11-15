document.querySelectorAll(".paginated-table").forEach(function (table) {
    const tbody = table.querySelector("tbody");
    const wrapper = table.closest(".list-table-wrapper");

    if (!tbody || !wrapper) return;

    let currentPage = 1;
    let pageSize = 25;

    const controls = document.createElement("div");
    controls.className = "table-pagination";
    controls.innerHTML = `
        <label>
            Rows per page
            <select aria-label="Rows per page">
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
            </select>
        </label>

        <span class="pagination-summary" role="status"></span>

        <nav class="pagination-buttons" aria-label="Table pagination">
            <button type="button" class="button button-small"
                    data-page="previous">
                Previous
            </button>
            <span class="pagination-page"></span>
            <button type="button" class="button button-small"
                    data-page="next">
                Next
            </button>
        </nav>
    `;

    wrapper.after(controls);

    const sizeSelect = controls.querySelector("select");
    const summary = controls.querySelector(".pagination-summary");
    const pageLabel = controls.querySelector(".pagination-page");
    const previousButton = controls.querySelector('[data-page="previous"]');
    const nextButton = controls.querySelector('[data-page="next"]');

    function renderPage() {
        // Read the current DOM order so header sorting applies to every page.
        const rows = Array.from(tbody.querySelectorAll(".list-row"));
        const matchingRows = rows.filter(function (row) {
            return row.dataset.filterMatch !== "false";
        });

        const total = matchingRows.length;
        const pageCount = Math.max(1, Math.ceil(total / pageSize));

        currentPage = Math.max(1, Math.min(currentPage, pageCount));

        const start = (currentPage - 1) * pageSize;
        const end = Math.min(start + pageSize, total);

        rows.forEach(function (row) {
            row.hidden = true;
            row.classList.remove("page-row-even");
        });

        matchingRows.slice(start, end).forEach(function (row, index) {
            row.hidden = false;
            row.classList.toggle("page-row-even", index % 2 === 1);
        });

        summary.textContent = total === 0
            ? "Showing 0 results"
            : `Showing ${start + 1}–${end} of ${total}`;

        pageLabel.textContent = total === 0
            ? "Page 0 of 0"
            : `Page ${currentPage} of ${pageCount}`;

        previousButton.disabled = total === 0 || currentPage === 1;
        nextButton.disabled = total === 0 || currentPage === pageCount;
    }

    sizeSelect.addEventListener("change", function () {
        pageSize = Number(sizeSelect.value);
        currentPage = 1;
        renderPage();
    });

    previousButton.addEventListener("click", function () {
        currentPage--;
        renderPage();
    });

    nextButton.addEventListener("click", function () {
        currentPage++;
        renderPage();
    });

    // Filters and sorting notify pagination after updating the rows.
    table.addEventListener("table-results-changed", function () {
        currentPage = 1;
        renderPage();
    });

    renderPage();
});