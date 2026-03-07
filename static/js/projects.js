function initMultiselects() {
    const multiselects = document.querySelectorAll('.custom-multiselect');

    multiselects.forEach(ms => {
        const nativeSelect = ms.previousElementSibling;
        if (nativeSelect && nativeSelect.tagName === 'SELECT') {
            nativeSelect.style.display = 'none';
        }
        ms.style.display = 'block';

        const header = ms.querySelector('.multiselect-header');
        const searchInput = ms.querySelector('.multiselect-search');
        const pillsContainer = ms.querySelector('.multiselect-pills');
        const options = ms.querySelectorAll('.multiselect-options input[type="checkbox"]');
        const selectAllBtn = ms.querySelector('.select-all');
        const optionLabels = ms.querySelectorAll('.multiselect-options .filter-list-item');

        header.addEventListener('click', (e) => {
            if(e.target.closest('.multiselect-pill')) return;
            
            if(e.target === searchInput) {
                ms.classList.add('open');
                return;
            }
            
            ms.classList.toggle('open');
            if (ms.classList.contains('open')) searchInput.focus();
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!ms.contains(e.target)) {
                ms.classList.remove('open');
            }
        });

        // Search filtering within the dropdown
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            ms.classList.add('open');
            optionLabels.forEach(label => {
                const text = label.textContent.toLowerCase();
                label.style.display = text.includes(term) ? 'flex' : 'none';
            });
        });

        // Generate pills and sync with native select
        const updatePills = () => {
            pillsContainer.innerHTML = '';
            let allChecked = true;
            let anyChecked = false;

            options.forEach(opt => {
                if (opt.checked) {
                    anyChecked = true;
                    const pill = document.createElement('span');
                    pill.className = 'multiselect-pill';
                    const labelText = opt.closest('.filter-list-item').querySelector('span').textContent;
                    
                    pill.innerHTML = `${labelText} <i class="fa-solid fa-xmark"></i>`;
                    
                    pill.querySelector('i').addEventListener('click', (e) => {
                        e.stopPropagation(); 
                        opt.checked = false;
                        updatePills();
                    });
                    
                    pillsContainer.appendChild(pill);
                } else {
                    allChecked = false;
                }
            });

            if (selectAllBtn) {
                selectAllBtn.checked = allChecked && options.length > 0;
            }
            
            searchInput.placeholder = anyChecked ? "" : "Search...";

            if (nativeSelect) {
                Array.from(nativeSelect.options).forEach(nativeOpt => {
                    const correspondingCheckbox = Array.from(options).find(cb => cb.value === nativeOpt.value);
                    if (correspondingCheckbox) {
                        nativeOpt.selected = correspondingCheckbox.checked;
                    }
                });
            }
        };

        options.forEach(opt => opt.addEventListener('change', updatePills));

        if (selectAllBtn) {
            selectAllBtn.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                options.forEach(opt => opt.checked = isChecked);
                updatePills();
            });
        }

        updatePills();
    });
}

function performProjectSearch() {
    const params = new URLSearchParams();

    const getValue = (id) => document.getElementById(id)?.value.trim();

    if (getValue("search-input")) params.append("search", getValue("search-input"));
    if (getValue("sort-select") !== "newest") params.append("sort", getValue("sort-select"));
    if (getValue("category-select")) params.append("category", getValue("category-select"));
    if (getValue("tags-input")) params.append("tech_stack", getValue("tags-input"));
    if (getValue("start-date")) params.append("start_date", getValue("start-date"));
    if (getValue("end-date")) params.append("end_date", getValue("end-date"));

    const activityCheckboxes = Array.from(document.querySelectorAll("#reading-time-multiselect .multiselect-options input[type='checkbox']:checked"));
    if (activityCheckboxes.length) {
        params.append("activity", activityCheckboxes.map(cb => cb.value).join(","));
    }

    const maturityCheckboxes = Array.from(document.querySelectorAll("#type-multiselect .multiselect-options input[type='checkbox']:checked"));
    if (maturityCheckboxes.length) {
        params.append("maturity", maturityCheckboxes.map(cb => cb.value).join(","));
    }

    location.href = params.toString() ? `/projects?${params.toString()}` : "/projects";
}

function restoreFilterState() {
	const params = new URLSearchParams(location.search);

	const searchInput = document.getElementById("search-input");
	const searchParam = params.get("search");
	if (searchInput && searchParam) {
		searchInput.value = searchParam;
	}

	const sortSelect = document.getElementById("sort-select");
	const sortParam = params.get("sort");
	if (sortSelect && sortParam) {
		sortSelect.value = sortParam;
	}

	const categorySelect = document.getElementById("category-select");
	const categoryParam = params.get("category");
	if (categorySelect && categoryParam) {
		categorySelect.value = categoryParam;
	}

	const tagInput = document.getElementById("tags-input");
	const tagsParam = params.get("tags");
	if (tagInput && tagsParam) {
		tagInput.value = tagsParam;
	}

	const startDateInput = document.getElementById("start-date");
	const endDateInput = document.getElementById("end-date");
	const startDateParam = params.get("start_date");
	const endDateParam = params.get("end_date");
	if (startDateInput && startDateParam) {
		startDateInput.value = startDateParam;
	}
	if (endDateInput && endDateParam) {
		endDateInput.value = endDateParam;
	}

	const readingTimeParam = params.get("reading_time");
	if (readingTimeParam) {
		const readingTimeValues = readingTimeParam.split(",");
		const readingTimeCheckboxes = document.querySelectorAll("#reading-time-multiselect .multiselect-options input[type='checkbox']");
		readingTimeCheckboxes.forEach(checkbox => {
			if (readingTimeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
	}

	const typeParam = params.get("type");
	if (typeParam) {
		const typeValues = typeParam.split(",");
		const typeCheckboxes = document.querySelectorAll("#type-multiselect .multiselect-options input[type='checkbox']");
		typeCheckboxes.forEach(checkbox => {
			if (typeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
	}
}

function initProjectSearch() {
	const searchInput = document.getElementById("search-input");
	const searchIcon = document.querySelector(".search-icon");
	const clearBtn = document.querySelector(".clear-filters-btn");
	const applyBtn = document.querySelector(".apply-filters-btn");
	const loadMoreBtn = document.getElementById("load-more-btn");
    
	if (!searchInput) return;
    
	if (searchIcon) {
		searchIcon.addEventListener("click", () => {
			performProjectSearch();
		});
	}
    
	searchInput.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			performProjectSearch();
		}
	});
    
	if (applyBtn) {
		applyBtn.addEventListener("click", performProjectSearch);
	}
    
	if (clearBtn) {
		clearBtn.addEventListener("click", () => {
			if (searchInput) searchInput.value = "";
			const filterDrawer = document.getElementById("filter-drawer");
			if (filterDrawer) {
				filterDrawer.querySelectorAll("input[type='text']").forEach(input => input.value = "");
				filterDrawer.querySelectorAll("input[type='date']").forEach(input => input.value = "");
				filterDrawer.querySelectorAll("input[type='checkbox']").forEach(checkbox => checkbox.checked = false);
				filterDrawer.querySelectorAll("select").forEach(select => select.value = select.options[0].value);
			}
			location.href = "/projects";
		});
	}
    
	if (loadMoreBtn) {
		loadMoreBtn.addEventListener("click", () => {
			const offset = loadMoreBtn.dataset.offset;
			const search = loadMoreBtn.dataset.search;
			const category = loadMoreBtn.dataset.category;
			const tags = loadMoreBtn.dataset.tags;
			const sort = loadMoreBtn.dataset.sort;
			const readingTime = loadMoreBtn.dataset.readingTime;
			const type = loadMoreBtn.dataset.type;
			const startDate = loadMoreBtn.dataset.startDate;
			const endDate = loadMoreBtn.dataset.endDate;
            
			const params = new URLSearchParams();
			if (search) params.append("search", search);
			if (category) params.append("category", category);
			if (tags) params.append("tags", tags);
			if (sort) params.append("sort", sort);
			if (readingTime) params.append("reading_time", readingTime);
			if (type) params.append("type", type);
			if (startDate) params.append("start_date", startDate);
			if (endDate) params.append("end_date", endDate);
			params.append("offset", offset);
            
			location.href = `/projects?${params.toString()}`;
		});
	}
    
	restoreFilterState();
    initMultiselects();
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", () => {
		initProjectSearch();
	});
} else {
	initProjectSearch();
}