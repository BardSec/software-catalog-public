document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("softwareGrid");
    const searchInput = document.getElementById("searchInput");
    const catalogCount = document.getElementById("catalogCount");
    const activeFiltersEl = document.getElementById("activeFilters");
    const clearFiltersBtn = document.getElementById("clearFilters");
    const filterToggle = document.getElementById("filterToggle");
    const filterSidebar = document.getElementById("filterSidebar");
    const filterClose = document.getElementById("filterClose");
    const checkboxes = document.querySelectorAll('.filter-option input[type="checkbox"]');

    let allSoftware = [];
    let debounceTimer = null;

    // Badge priority for card display (show these types on cards)
    const CARD_BADGE_TYPES = ["dpa_status", "cost", "roster", "access"];

    // Fetch all software on load
    fetchSoftware();

    // Event listeners
    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(filterAndRender, 250);
    });

    checkboxes.forEach(cb => cb.addEventListener("change", filterAndRender));

    clearFiltersBtn.addEventListener("click", () => {
        searchInput.value = "";
        checkboxes.forEach(cb => (cb.checked = false));
        filterAndRender();
    });

    filterToggle.addEventListener("click", () => filterSidebar.classList.add("open"));
    filterClose.addEventListener("click", () => filterSidebar.classList.remove("open"));

    async function fetchSoftware() {
        try {
            const resp = await fetch("/api/software");
            if (!resp.ok) throw new Error("Failed to load");
            allSoftware = await resp.json();
            filterAndRender();
        } catch (err) {
            grid.innerHTML = '<div class="no-results">Failed to load catalog. Please refresh.</div>';
        }
    }

    function filterAndRender() {
        const query = searchInput.value.toLowerCase().trim();
        const selectedCats = new Set(
            Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => parseInt(cb.value))
        );

        let filtered = allSoftware;

        // Text search
        if (query) {
            filtered = filtered.filter(s =>
                s.name.toLowerCase().includes(query) ||
                s.tagline.toLowerCase().includes(query)
            );
        }

        // Category filter (AND logic - must match all selected categories)
        if (selectedCats.size > 0) {
            filtered = filtered.filter(s => {
                const catIds = new Set(s.categories.map(c => c.id));
                for (const id of selectedCats) {
                    if (!catIds.has(id)) return false;
                }
                return true;
            });
        }

        renderGrid(filtered);
        renderActiveFilters(selectedCats);
        catalogCount.textContent = `${filtered.length} of ${allSoftware.length} items`;
    }

    function renderGrid(items) {
        if (items.length === 0) {
            grid.innerHTML = '<div class="no-results">No software matches your search or filters.</div>';
            return;
        }

        grid.innerHTML = items.map(s => {
            const logoHtml = s.logo
                ? `<img class="card-logo" src="${escapeHtml(s.logo)}" alt="" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                   <div class="logo-placeholder" style="display:none;">${escapeHtml(s.name[0])}</div>`
                : `<div class="logo-placeholder">${escapeHtml(s.name[0])}</div>`;

            // Show priority badges on card
            const badges = s.categories
                .filter(c => CARD_BADGE_TYPES.includes(c.type))
                .map(c => `<span class="badge badge-${c.type}" data-name="${escapeHtml(c.name)}">${escapeHtml(c.name)}</span>`)
                .join("");

            return `
                <a href="/software/${s.id}" class="software-card ${s.featured ? "featured" : ""}">
                    <div class="card-header">
                        ${logoHtml}
                        <div class="card-name">${escapeHtml(s.name)}</div>
                    </div>
                    <div class="card-tagline">${escapeHtml(s.tagline)}</div>
                    <div class="card-badges">${badges}</div>
                </a>
            `;
        }).join("");
    }

    function renderActiveFilters(selectedCats) {
        if (selectedCats.size === 0) {
            activeFiltersEl.innerHTML = "";
            return;
        }

        const labels = [];
        checkboxes.forEach(cb => {
            if (cb.checked) {
                const badge = cb.parentElement.querySelector(".badge");
                labels.push({
                    id: parseInt(cb.value),
                    name: badge ? badge.textContent : cb.value,
                });
            }
        });

        activeFiltersEl.innerHTML = labels
            .map(l => `<button class="active-filter" data-id="${l.id}">${escapeHtml(l.name)} &times;</button>`)
            .join("");

        activeFiltersEl.querySelectorAll(".active-filter").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.dataset.id;
                checkboxes.forEach(cb => {
                    if (cb.value === id) cb.checked = false;
                });
                filterAndRender();
            });
        });
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str || "";
        return div.innerHTML;
    }
});
