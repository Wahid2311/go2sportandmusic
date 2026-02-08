// =======================
// Categories Data
// =======================
let NAV_CATEGORIES = [];

// Fetch categories from API
async function fetchNavCategories() {
    try {
        // First, fetch event categories from Django
        const categoriesResponse = await fetch('/api/categories/list/');
        if (categoriesResponse.ok) {
            const categoriesData = await categoriesResponse.json();
            
            // Map categories to NAV_CATEGORIES format
            NAV_CATEGORIES = categoriesData.map(cat => ({
                id: cat.id,
                name: cat.name,
                slug: cat.slug,
                icon: cat.icon,
                url: `/events/all/?category=${cat.slug}`,
                countries: []
            }));
        } else {
            // Fallback to default categories
            NAV_CATEGORIES = [
                { id: 1, name: "Football", slug: "football", icon: "bi-soccer", url: "/events/all/?category=football", countries: [] },
                { id: 2, name: "Formula 1", slug: "formula-1", icon: "bi-speedometer2", url: "/events/all/?category=formula-1", countries: [] },
                { id: 3, name: "MotoGP", slug: "motogp", icon: "bi-speedometer2", url: "/events/all/?category=motogp", countries: [] },
                { id: 4, name: "Tennis", slug: "tennis", icon: "bi-racquet", url: "/events/all/?category=tennis", countries: [] },
                { id: 5, name: "Other events", slug: "other-events", icon: "bi-calendar-event", url: "/events/all/?category=other-events", countries: [] }
            ];
        }

        renderNavbarCategories();
    } catch (error) {
        console.error('Error fetching categories:', error);
        // Fallback to default categories
        NAV_CATEGORIES = [
            { id: 1, name: "Football", slug: "football", icon: "bi-soccer", url: "/events/all/?category=football", countries: [] },
            { id: 2, name: "Formula 1", slug: "formula-1", icon: "bi-speedometer2", url: "/events/all/?category=formula-1", countries: [] },
            { id: 3, name: "MotoGP", slug: "motogp", icon: "bi-speedometer2", url: "/events/all/?category=motogp", countries: [] },
            { id: 4, name: "Tennis", slug: "tennis", icon: "bi-racquet", url: "/events/all/?category=tennis", countries: [] },
            { id: 5, name: "Other events", slug: "other-events", icon: "bi-calendar-event", url: "/events/all/?category=other-events", countries: [] }
        ];
        renderNavbarCategories();
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
        a.href = category.url || "#";
        a.innerHTML = `
            <span>${category.name}</span>
        `;

        li.appendChild(a);
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
