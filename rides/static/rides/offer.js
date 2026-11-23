"use strict";
(() => {
    const rows = document.getElementById("waypoint-rows");
    const total = document.getElementById("id_waypoints-TOTAL_FORMS");
    const template = document.getElementById("empty-stop");
    const renumber = () => {
        Array.from(rows.children).forEach((row, index) => {
            row.querySelectorAll("[name], [id], label[for]").forEach((element) => {
                ["name", "id", "for"].forEach((attribute) => {
                    const value = element.getAttribute(attribute);
                    if (value) element.setAttribute(attribute, value.replace(/waypoints-(?:\d+|__prefix__)-/g, `waypoints-${index}-`));
                });
            });
        });
        total.value = rows.children.length;
        document.getElementById("stop-count").textContent = `${total.value} parada(s) intermediária(s).`;
    };
    document.getElementById("add-stop").addEventListener("click", () => {
        rows.appendChild(template.content.cloneNode(true));
        renumber();
        rows.lastElementChild.querySelector("select").focus();
    });
    rows.addEventListener("click", (event) => {
        if (event.target.matches("[data-remove-stop]")) {
            event.target.closest(".waypoint-row").remove();
            renumber();
        }
    });
    renumber();
})();
