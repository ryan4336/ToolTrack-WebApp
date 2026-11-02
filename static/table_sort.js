
document.addEventListener("DOMContentLoaded", function () {
    const tables = document.querySelectorAll(".sortable-table");

    const collator = new Intl.Collator(undefined, {
        numeric: true,
        sensitivity: "base"
    });

    tables.forEach(function (table) {
        const tbody = table.querySelector("tbody");
        const headers = table.querySelectorAll("thead th[data-sort-type]");

        if (!tbody) return;

        // Remember the original order for stable sorting.
        Array.from(tbody.rows).forEach(function (row, index) {
            row.dataset.originalIndex = index;
        });

        headers.forEach(function (header) {
            header.classList.add("sortable-header");
            header.tabIndex = 0;
            header.setAttribute("role", "button");
            header.setAttribute("aria-label", "Sort by " + header.textContent.trim());

            function sortColumn() {
                const columnIndex = header.cellIndex;
                const sortType = header.dataset.sortType;

                const direction =
                    header.dataset.sortDirection === "asc" ? "desc" : "asc";

                // Clear sorting indicators from other columns.
                headers.forEach(function (otherHeader) {
                    otherHeader.removeAttribute("data-sort-direction");
                    otherHeader.setAttribute("aria-sort", "none");
                });

                header.dataset.sortDirection = direction;
                header.setAttribute(
                    "aria-sort",
                    direction === "asc" ? "ascending" : "descending"
                );

                const rows = Array.from(tbody.rows);

                rows.sort(function (rowA, rowB) {
                    const cellA = rowA.cells[columnIndex];
                    const cellB = rowB.cells[columnIndex];

                    const valueA = (cellA.dataset.sortValue ?? cellA.textContent).trim();
                    const valueB = (cellB.dataset.sortValue ?? cellB.textContent).trim();

                    // Empty values always go last.
                    const emptyA = valueA === "" || valueA === "—";
                    const emptyB = valueB === "" || valueB === "—";

                    if (emptyA && !emptyB) return 1;
                    if (!emptyA && emptyB) return -1;

                    let comparison = 0;

                    if (sortType === "number" || sortType === "currency") {
                        const numberA = Number(valueA.replace(/[$,]/g, ""));
                        const numberB = Number(valueB.replace(/[$,]/g, ""));

                        if (Number.isNaN(numberA) && !Number.isNaN(numberB)) return 1;
                        if (!Number.isNaN(numberA) && Number.isNaN(numberB)) return -1;

                        comparison = numberA - numberB;
                    } else if (sortType === "date") {
                        const dateA = Date.parse(valueA);
                        const dateB = Date.parse(valueB);

                        if (Number.isNaN(dateA) && !Number.isNaN(dateB)) return 1;
                        if (!Number.isNaN(dateA) && Number.isNaN(dateB)) return -1;

                        comparison = dateA - dateB;
                    } else {
                        comparison = collator.compare(valueA, valueB);
                    }

                    if (comparison === 0 || Number.isNaN(comparison)) {
                        return Number(rowA.dataset.originalIndex) -
                               Number(rowB.dataset.originalIndex);
                    }

                    return direction === "asc" ? comparison : -comparison;
                });

                // Reorder existing DOM rows without changing database records.
                rows.forEach(function (row) {
                    tbody.appendChild(row);
                });
            }

            header.addEventListener("click", sortColumn);

            // Allow keyboard sorting with Enter or Space.
            header.addEventListener("keydown", function (event) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    sortColumn();
                }
            });
        });
    });
});
