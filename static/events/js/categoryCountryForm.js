// Countries will be loaded from global scope
let container;
let hiddenInput;
let COUNTRIES = window.COUNTRIES || [];

/* ---------- COUNTRY OPTIONS ---------- */

function countryOptions() {
    return `
        <option value="">Select country</option>
        ${COUNTRIES.map(c => `
            <option value="${c.label}" data-code="${c.code}">
                ${c.label}
            </option>
        `).join("")}
    `;
}

/* ---------- API CALLS ---------- */

async function callCreateAPI(type, btnElement) {
    console.log("API called for:", type);

    const section = btnElement.closest(`.${type}-section`);
    const countrySelect = section.querySelector(".country-select");
    const nameInput = section.querySelector(".name-input");
    const flag = section.querySelector(".country-flag");

    const country = countrySelect.value;
    const name = nameInput.value;

    if (!country || !name) {
        showToast("Please select a country and enter a name.", "error");
        return;
    }

    // Loading State
    const originalIcon = btnElement.innerHTML;
    btnElement.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`;
    btnElement.disabled = true;

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch('/api/categories/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type: type,
                country: country,
                name: name
            })
        });

        const data = await response.json();

        if (data.success) {
            // Clear inputs on success
            countrySelect.value = "";
            nameInput.value = "";
            if (flag) flag.style.display = "none";
            showToast(`${type.slice(0, -1).charAt(0).toUpperCase() + type.slice(1, -1)} added successfully!`, "success");
        } else {
            showToast(`Error: ${data.error}`, "error");
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred while saving.', "error");
    } finally {
        // Restore Button State
        btnElement.innerHTML = originalIcon;
        btnElement.disabled = false;
    }

    syncPayload();
}

function showToast(message, type = "success") {
    let toastContainer = document.querySelector('.alert-messages');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'alert-messages';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const alertClass = type === 'error' ? 'alert-error' : 'alert-success';

    toast.className = `alert ${alertClass} alert-dismissible fade show`;
    toast.role = 'alert';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    toastContainer.appendChild(toast);

    // Auto dismiss after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 150);
    }, 3000);
}

/* ---------- ROW GENERATION ---------- */

function createSingleRow(type) {
    const wrapper = document.createElement("div");
    wrapper.className = `${type}-section`;

    wrapper.innerHTML = `
        <div class="d-flex gap-2 align-items-center mb-3">
            <div class="country-select-wrapper">
                <img class="country-flag" width="20" alt="" />
                <select class="form-select country-select">
                    ${countryOptions()}
                </select>
            </div>

            <input
                type="text"
                class="form-control name-input"
                placeholder="Enter ${type.slice(0, -1)}"
            />

            <button
                type="button"
                class="btn btn-outline-primary btn-sm add-row"
                data-type="${type}">
                <i class="bi bi-plus"></i>
            </button>
        </div>
    `;

    return wrapper;
}

/* ---------- SECTION GENERATION ---------- */

function renderSection(title, type) {
    const section = document.createElement("div");
    section.className = "section-card mb-4";
    section.style.padding = "15px";
    section.style.borderRadius = "10px";

    section.innerHTML = `<h6 class="mb-3">${title}</h6>`;
    section.appendChild(createSingleRow(type));

    return section;
}

/* ---------- TABLES (REAL DATA) ---------- */
let categoryData = {
    teams: {},
    tournaments: {}
};

async function fetchCategories() {
    try {
        const response = await fetch('/api/categories/list/');
        if (response.ok) {
            categoryData = await response.json();
            renderTables();
        } else {
            console.error('Failed to fetch categories');
        }
    } catch (error) {
        console.error('Error fetching categories:', error);
    }
}

function renderTableSection(title, data) {
    if (Object.keys(data).length === 0) {
        return `<p class="text-muted">No ${title.toLowerCase()} added yet.</p>`;
    }

    let rows = '';
    for (const [country, items] of Object.entries(data)) {
        const pills = items.map(item => `
            <span class="badge bg-${title === 'Teams' ? 'primary' : 'success'} me-2">
                ${item.name}
            </span>
        `).join("");

        rows += `
            <tr>
                <td>${country}</td>
                <td>${pills}</td>
            </tr>
        `;
    }

    return `
        <h6>${title}</h6>
        <table class="table table-bordered mb-4 align-middle">
            <thead>
                <tr>
                    <th style="width: 180px">Country</th>
                    <th>${title}</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

function renderTables() {
    let tables = document.getElementById("tablesWrapper");

    if (!tables) {
        tables = document.createElement("div");
        tables.id = "tablesWrapper";
        tables.className = "mt-4";
        container.appendChild(tables);
    }

    tables.innerHTML = `
        ${renderTableSection('Teams', categoryData.teams)}
        ${renderTableSection('Tournaments', categoryData.tournaments)}
    `;
}

/* ---------- PAYLOAD SYNC ---------- */

function syncPayload() {
    const data = {
        teams: [],
        tournaments: []
    };
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(data);
    }
}

/* ---------- INIT ---------- */

console.log("Script file loaded - defining DOMContentLoaded listener");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOMContentLoaded fired!");
    console.log("Initializing Category Form...");

    container = document.getElementById("categoryCountryForm");
    hiddenInput = document.getElementById("teamsTournamentsInput");

    console.log("Container:", container);
    console.log("hiddenInput:", hiddenInput);
    console.log("COUNTRIES array length:", COUNTRIES ? COUNTRIES.length : 0);

    if (!container) {
        console.error("Container #categoryCountryForm not found!");
        return;
    }

    console.log("Rendering sections...");
    // Render static input sections
    container.appendChild(renderSection("Tournaments", "tournaments"));
    container.appendChild(renderSection("Teams", "teams"));
    console.log("Sections rendered!");

    // Initial fetch of existing categories
    console.log("Fetching categories...");
    fetchCategories();

    /* ---------- EVENT LISTENERS ---------- */

    // Add Category Click
    container.addEventListener("click", e => {
        const addBtn = e.target.closest(".add-row");
        if (!addBtn) return;

        const type = addBtn.dataset.type;
        callCreateAPI(type, addBtn).then(() => {
            fetchCategories(); // Refresh list after add
        });
    });

    // Country selection change (for flags)
    container.addEventListener("change", e => {
        const select = e.target.closest(".country-select");
        if (!select) return;

        const flag = select
            .closest(".country-select-wrapper")
            .querySelector(".country-flag");

        const code = select.selectedOptions[0]?.dataset.code;

        if (code) {
            flag.src = `https://flagcdn.com/w20/${code.toLowerCase()}.png`;
            flag.style.display = "block";
        } else {
            flag.style.display = "none";
        }
    });

    console.log("Category Form Initialized.");
});
