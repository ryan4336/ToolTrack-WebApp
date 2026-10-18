// Get the tool and condition dropdowns
const toolSelect = document.getElementById("asset-id");
const conditionSelect = document.getElementById("condition");

// Update the condition whenever a different tool is selected
toolSelect.addEventListener("change", function () {
    const selectedTool = toolSelect.options[toolSelect.selectedIndex];
    const condition = selectedTool.dataset.condition;

    // Require a manual selection if no tool is selected or condition is Unknown
    if (!condition || condition === "Unknown") {
        conditionSelect.value = "";
    } else {
        conditionSelect.value = condition;
    }
});