// =======================
// Categories Data
// =======================
let NAV_CATEGORIES = [
    {
        id: 1,
        name: "Football",
        countries: []
    }
];

// Fetch categories from API
async function fetchNavCategories() {
    try {
        const response = await fetch('/api/categories/list/');
        if (!response.ok) {
            return;
        }

        const data = await response.json();

        const countriesMap = {};

        for (const [country, teams] of Object.entries(data.teams)) {
            if (!countriesMap[country]) {
                countriesMap[country] = {
                    name: country,
                    flag: getCountryFlag(country),
                    tournaments: [],
                    teams: []
                };
            }
            countriesMap[country].teams = teams.map(t => t.name);
        }

        for (const [country, tournaments] of Object.entries(data.tournaments)) {
            if (!countriesMap[country]) {
                countriesMap[country] = {
                    name: country,
                    flag: getCountryFlag(country),
                    tournaments: [],
                    teams: []
                };
            }
            countriesMap[country].tournaments = tournaments.map(t => t.name);
        }

        const countries = Object.values(countriesMap);

        NAV_CATEGORIES[0].countries = countries;
        renderNavbarCategories();
    } catch (error) {
    }
}

function getCountryFlag(countryName) {
    const COUNTRIES = window.COUNTRIES || [];

    const country = COUNTRIES.find(c =>
        c.label.toLowerCase() === countryName.toLowerCase()
    );

    if (country) {
        return `https://flagcdn.com/w40/${country.code.toLowerCase()}.png`;
    }

    const countryCodeMap = {
        'United Kingdom': 'gb',
        'UK': 'gb',
        'United States': 'us',
        'USA': 'us'
    };

    const code = countryCodeMap[countryName] || countryName.toLowerCase().slice(0, 2);
    return `https://flagcdn.com/w40/${code}.png`;
}


// =======================
// Navbar Rendering
// =======================
document.addEventListener('DOMContentLoaded', function () {
    renderNavbarCategories();
    fetchNavCategories();
});

function renderNavbarCategories() {
    const navbar = document.getElementById("categoryNavbar");
    if (!navbar) return;

    navbar.innerHTML = "";

    NAV_CATEGORIES.forEach(category => {
        const li = document.createElement("li");
        li.className = "nav-item";

        const a = document.createElement("a");
        a.className = "nav-link";
        a.href = "#";
        a.innerHTML = `
            <span>${category.name}</span>
            ${category.countries && category.countries.length > 0 ? `<i class="bi bi-chevron-down chevron"></i>` : ""}
        `;

        li.appendChild(a);

        if (category.countries && category.countries.length > 0) {
            const dropdown = document.createElement("div");
            dropdown.className = "category-dropdown";

            category.countries.forEach(country => {
                const item = document.createElement("div");
                item.className = "country-item position-relative";

                item.innerHTML = `
                    <img src="${country.flag}" class="country-flag" alt="${country.name}">
                    <span class="country-name">${country.name}</span>
                    <i class="bi bi-chevron-right country-arrow"></i>
                `;

                const submenu = document.createElement("div");
                submenu.className = "country-submenu";

                submenu.innerHTML = `
                    <div class="submenu-section">
                        <div class="submenu-title">${country.tournaments.length > 0 ? "Tournaments" : ""}</div>
                        <div class="submenu-list">
                            ${country.tournaments.map(t =>
                    `<div class="submenu-item" data-type="tournament" data-value="${t}" style="cursor: pointer;"><i class="bi bi-chevron-right"></i> ${t}</div>`
                ).join("")}
                        </div>
                    </div>

                    <div class="submenu-section">
                        <div class="submenu-title">${country.teams.length > 0 ? "Teams" : ""}</div>
                        <div class="submenu-list">
                            ${country.teams.map(t =>
                    `<div class="submenu-item" data-type="team" data-value="${t}" style="cursor: pointer;"><i class="bi bi-chevron-right"></i> ${t}</div>`
                ).join("")}
                        </div>
                    </div>
                `;

                submenu.querySelectorAll('.submenu-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const type = item.dataset.type;
                        const value = encodeURIComponent(item.dataset.value);

                        if (type === 'tournament') {
                            window.location.href = `/events/search-results/?query=${value}`;
                        } else if (type === 'team') {
                            window.location.href = `/events/search-results/?query=${value}`;
                        }
                    });
                });

                item.appendChild(submenu);
                dropdown.appendChild(item);
            });

            li.appendChild(dropdown);
        }

        navbar.appendChild(li);
    });
}


// =======================
// Search Overlay Logic  
// =======================
document.addEventListener('DOMContentLoaded', function () {
    const searchTrigger = document.getElementById('searchTrigger');
    const searchOverlay = document.getElementById('searchOverlay');
    const closeSearch = document.getElementById('closeSearch');
    const searchModalInput = document.getElementById('searchModalInput');

    if (searchTrigger) {
        searchTrigger.addEventListener('click', () => {
            searchOverlay.classList.add('active');
            setTimeout(() => searchModalInput?.focus(), 300);
        });
    }

    if (closeSearch) {
        closeSearch.addEventListener('click', () => {
            searchOverlay.classList.remove('active');
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            searchOverlay.classList.remove('active');
        }
    });

    if (searchOverlay) {
        searchOverlay.addEventListener('click', (e) => {
            if (e.target === searchOverlay) {
                searchOverlay.classList.remove('active');
            }
        });
    }

    initSearchAutocomplete('.search-modal-input', '#navbar-search-results');
});


// =======================
// Date Helper
// =======================
function parseEventDate(dateStr) {
    return new Date(dateStr + " 00:00:00");
}


// =======================
// Search Autocomplete
// =======================
function initSearchAutocomplete(inputSelector, resultsContainer) {
    const searchInput = document.querySelector(inputSelector);
    const resultsDiv = document.querySelector(resultsContainer);

    if (!searchInput || !resultsDiv) return;

    let timeoutId;

    searchInput.addEventListener('input', function () {
        clearTimeout(timeoutId);
        const query = this.value.trim();

        if (query.length < 2) {
            resultsDiv.innerHTML = '';
            return;
        }

        resultsDiv.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
            </div>
        `;

        timeoutId = setTimeout(() => {
            fetch(`/events/search-autocomplete/?query=${encodeURIComponent(query)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(res => {
                    if (!res.ok) throw new Error('Network error');
                    return res.json();
                })
                .then(data => {
                    if (!data.length) {
                        resultsDiv.innerHTML = `
                            <div class="no-results">
                                No events found matching "${query}"
                            </div>
                        `;
                        return;
                    }

                    const now = new Date();

                    const sortedEvents = data.sort((a, b) => {
                        const dateA = parseEventDate(a.date);
                        const dateB = parseEventDate(b.date);

                        const isAFuture = dateA >= now;
                        const isBFuture = dateB >= now;

                        if (isAFuture && !isBFuture) return -1;
                        if (!isAFuture && isBFuture) return 1;

                        if (isAFuture && isBFuture) {
                            return dateA - dateB;
                        }

                        return dateB - dateA;
                    });

                    resultsDiv.innerHTML = sortedEvents.map(event => `
                        <a href="${event.url}" class="autocomplete-item">
                            <div class="ac-event-name">${event.name}</div>
                            <div class="ac-event-details">
                                <span>${event.category}</span>
                                <span>${event.date}</span>
                                <span>$${event.min_price} - $${event.max_price}</span>
                            </div>
                        </a>
                    `).join('');
                })
                .catch(() => {
                    resultsDiv.innerHTML = `
                        <div class="no-results">
                            Error loading search results
                        </div>
                    `;
                });
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.innerHTML = '';
        }
    });

    searchInput.addEventListener('change', function () {
        if (!this.value.trim()) {
            resultsDiv.innerHTML = '';
        }
    });
}
