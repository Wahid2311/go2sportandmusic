/**
 * Stadium SVG Interactive Viewer
 * Handles rendering and interaction with SVG stadium maps
 */

class StadiumSVGViewer {
    constructor(containerId, stadiumKey, sectionsData, onSectionClick) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }

        this.stadiumKey = stadiumKey;
        this.sectionsData = sectionsData;
        this.onSectionClick = onSectionClick || this.defaultSectionClick.bind(this);
        this.selectedSections = new Set();
        this.tooltip = null;

        this.init();
    }

    init() {
        this.loadAndRenderSVG();
    }

    async loadAndRenderSVG() {
        try {
            // Load SVG from static file
            const response = await fetch(`/static/events/stadiums/svg/${this.stadiumKey}.svg`);
            if (!response.ok) {
                throw new Error(`Failed to load SVG: ${response.statusText}`);
            }

            const svgContent = await response.text();
            this.container.innerHTML = svgContent;

            // Initialize after SVG is loaded
            this.attachEventListeners();
            this.applySectionColors();
            this.createTooltip();
        } catch (error) {
            console.error('Error loading SVG:', error);
            this.showFallbackMessage();
        }
    }

    showFallbackMessage() {
        this.container.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #666;">
                <p>Interactive stadium map not available</p>
            </div>
        `;
    }

    applySectionColors() {
        this.sectionsData.forEach(section => {
            const paths = this.getSectionPaths(section.svg_section_key);
            paths.forEach(path => {
                // Apply color with transparency
                path.style.fill = section.color + '99';
                path.dataset.sectionId = section.id;
                path.dataset.sectionName = section.name;
                path.dataset.sectionColor = section.color;
            });
        });
    }

    getSectionPaths(sectionKey) {
        if (!sectionKey) return [];

        // Find all SVG paths with matching data-section or data-tags
        const selector = `[data-section="${sectionKey}"], [data-tags*="${sectionKey}"]`;
        return Array.from(this.container.querySelectorAll(selector));
    }

    attachEventListeners() {
        const allPaths = this.container.querySelectorAll('#shapes path, #shapes [data-section]');

        allPaths.forEach(path => {
            path.style.cursor = 'pointer';
            path.style.transition = 'all 0.2s ease';

            path.addEventListener('click', (e) => {
                this.handlePathClick(e);
            });

            path.addEventListener('mouseenter', (e) => {
                this.handleMouseEnter(e);
            });

            path.addEventListener('mouseleave', () => {
                this.handleMouseLeave();
            });
        });
    }

    handlePathClick(event) {
        const path = event.target;
        const sectionId = path.dataset.sectionId;
        const sectionName = path.dataset.sectionName;
        const svgSectionKey = path.getAttribute('data-section');

        if (!sectionId) {
            console.log('Clicked on unmapped section:', svgSectionKey);
            return;
        }

        const sectionPaths = this.container.querySelectorAll(`[data-section-id="${sectionId}"]`);

        // Toggle selection
        if (this.selectedSections.has(sectionId)) {
            this.selectedSections.delete(sectionId);
            sectionPaths.forEach(p => p.classList.remove('selected'));
        } else {
            this.selectedSections.add(sectionId);
            sectionPaths.forEach(p => p.classList.add('selected'));
        }

        // Trigger callback
        this.onSectionClick(Array.from(this.selectedSections));
    }

    handleMouseEnter(event) {
        const path = event.target;
        const sectionId = path.dataset.sectionId;
        const sectionName = path.dataset.sectionName;

        if (sectionId) {
            const sectionPaths = this.container.querySelectorAll(`[data-section-id="${sectionId}"]`);

            sectionPaths.forEach(p => {
                if (!p.classList.contains('selected')) {
                    p.style.opacity = '0.8';
                    p.style.filter = 'brightness(1.1)';
                }
            });
        } else {
            if (!path.classList.contains('selected')) {
                path.style.opacity = '0.8';
                path.style.filter = 'brightness(1.1)';
            }
        }

        // Show tooltip
        if (sectionName) {
            this.showTooltip(event, sectionName);
        }
    }

    handleMouseLeave(event) {
        // Remove hover effects from all paths
        // We can just clear styles for non-selected paths
        const allPaths = this.container.querySelectorAll('#shapes path');
        allPaths.forEach(path => {
            if (!path.classList.contains('selected')) {
                path.style.opacity = '';
                path.style.filter = '';
            }
        });

        this.hideTooltip();
    }

    createTooltip() {
        if (this.tooltip) return;

        this.tooltip = document.createElement('div');
        this.tooltip.id = 'svg-stadium-tooltip';
        this.tooltip.style.cssText = `
            position: fixed;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            z-index: 10000;
            display: none;
            white-space: nowrap;
        `;
        document.body.appendChild(this.tooltip);
    }

    showTooltip(event, text) {
        if (!this.tooltip) return;

        this.tooltip.textContent = text;
        this.tooltip.style.display = 'block';
        this.tooltip.style.left = (event.clientX + 10) + 'px';
        this.tooltip.style.top = (event.clientY + 10) + 'px';
    }

    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.style.display = 'none';
        }
    }

    defaultSectionClick(selectedSectionIds) {
        console.log('Selected sections:', selectedSectionIds);

        // Dispatch custom event
        const event = new CustomEvent('stadium-section-filter', {
            detail: { sectionIds: selectedSectionIds }
        });
        window.dispatchEvent(event);
    }

    clearSelection() {
        this.selectedSections.clear();
        const allPaths = this.container.querySelectorAll('#shapes path.selected');
        allPaths.forEach(path => {
            path.classList.remove('selected');
        });
    }

    destroy() {
        if (this.tooltip && this.tooltip.parentNode) {
            this.tooltip.parentNode.removeChild(this.tooltip);
        }
    }
}

// Export for use in modules or make globally available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StadiumSVGViewer;
} else {
    window.StadiumSVGViewer = StadiumSVGViewer;
}
