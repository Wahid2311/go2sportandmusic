/**
 * Custom Country Dropdown with Flags
 * Creates a searchable dropdown that displays country flags
 */

class CustomCountryDropdown {
    constructor(container, options = {}) {
        this.container = container;
        this.countries = window.COUNTRIES || [];
        this.selectedCountry = null;
        this.isOpen = false;
        this.searchTerm = '';
        this.onSelect = options.onSelect || (() => { });

        this.render();
        this.attachEvents();
    }

    render() {
        this.container.innerHTML = `
            <div class="custom-country-dropdown">
                <div class="dropdown-trigger">
                    <div class="selected-country">
                        <span >Select country</span>
                    </div>
                    <i class="bi bi-chevron-down dropdown-arrow"></i>
                </div>
                <div class="dropdown-menu">
                    <div class="dropdown-search">
                        <i class="bi bi-search"></i>
                        <input type="text" class="search-input" placeholder="Search countries...">
                    </div>
                    <div class="dropdown-list"></div>
                </div>
            </div>
        `;

        this.trigger = this.container.querySelector('.dropdown-trigger');
        this.menu = this.container.querySelector('.dropdown-menu');
        this.searchInput = this.container.querySelector('.search-input');
        this.list = this.container.querySelector('.dropdown-list');
        this.arrow = this.container.querySelector('.dropdown-arrow');
        this.selectedDisplay = this.container.querySelector('.selected-country');

        this.renderList();
    }

    renderList(filter = '') {
        const filtered = this.countries.filter(c =>
            c.label.toLowerCase().includes(filter.toLowerCase())
        );

        if (filtered.length === 0) {
            this.list.innerHTML = `
                <div class="dropdown-item no-results">
                    <span>No countries found</span>
                </div>
            `;
            return;
        }

        this.list.innerHTML = filtered.map(country => `
            <div class="dropdown-item" data-code="${country.code}" data-label="${country.label}">
                <img src="https://flagcdn.com/w40/${country.code.toLowerCase()}.png" 
                     class="country-flag-option" 
                     alt="${country.label}"
                     onerror="this.style.display='none'">
                <span class="country-name">${country.label}</span>
            </div>
        `).join('');
    }

    attachEvents() {
        // Toggle dropdown
        this.trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });

        // Search functionality
        this.searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.renderList(this.searchTerm);
        });

        // Item selection
        this.list.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item && !item.classList.contains('no-results')) {
                const code = item.dataset.code;
                const label = item.dataset.label;
                this.selectCountry(code, label);
            }
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.close();
            }
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.menu.classList.add('active');
        this.arrow.style.transform = 'rotate(180deg)';
        this.searchInput.focus();
        this.searchInput.value = '';
        this.renderList('');
    }

    close() {
        this.isOpen = false;
        this.menu.classList.remove('active');
        this.arrow.style.transform = 'rotate(0deg)';
    }

    selectCountry(code, label) {
        this.selectedCountry = { code, label };

        // Update display
        this.selectedDisplay.innerHTML = `
            <img src="https://flagcdn.com/w40/${code.toLowerCase()}.png" 
                 class="country-flag-selected" 
                 alt="${label}">
            <span>${label}</span>
        `;

        this.close();
        this.onSelect({ code, label });
    }

    getValue() {
        return this.selectedCountry;
    }

    setValue(countryLabel) {
        const country = this.countries.find(c => c.label === countryLabel);
        if (country) {
            this.selectCountry(country.code, country.label);
        }
    }

    reset() {
        this.selectedCountry = null;
        this.selectedDisplay.innerHTML = '<span>Select country</span>';
    }
}

// Export for use in other scripts
window.CustomCountryDropdown = CustomCountryDropdown;
