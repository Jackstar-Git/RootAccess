function initMultiselects() {
    const multiselects = document.querySelectorAll(".custom-multiselect");

    multiselects.forEach(ms => {
        const nativeSelect = ms.previousElementSibling;
        if (nativeSelect && nativeSelect.tagName === "SELECT") {
            nativeSelect.style.display = "none";
        }
        ms.style.display = "block";

        const header = ms.querySelector(".multiselect-header");
        const searchInput = ms.querySelector(".multiselect-search");
        const pillsContainer = ms.querySelector(".multiselect-pills");
        const options = ms.querySelectorAll('.multiselect-options input[type="checkbox"]');
        const selectAllBtn = ms.querySelector(".select-all");
        const optionLabels = ms.querySelectorAll(".multiselect-options .filter-list-item");

        header.addEventListener("click", (e) => {
            if(e.target.closest(".multiselect-pill")) return;
            
            if(e.target === searchInput) {
                ms.classList.add("open");
                return;
            }
            
            ms.classList.toggle("open");
            if (ms.classList.contains("open")) searchInput.focus();
        });

        document.addEventListener("click", (e) => {
            if (!ms.contains(e.target)) {
                ms.classList.remove("open");
            }
        });

        searchInput.addEventListener("input", (e) => {
            const term = e.target.value.toLowerCase();
            ms.classList.add("open");
            optionLabels.forEach(label => {
                const text = label.textContent.toLowerCase();
                label.style.display = text.includes(term) ? "flex" : "none";
            });
        });

        const updatePills = () => {
            pillsContainer.innerHTML = "";
            let allChecked = true;
            let anyChecked = false;

            options.forEach(opt => {
                if (opt.checked) {
                    anyChecked = true;
                    const pill = document.createElement("span");
                    pill.className = "multiselect-pill";
                    const labelText = opt.closest(".filter-list-item").querySelector("span").textContent;
                    
                    pill.innerHTML = `${labelText} <i class="fa-solid fa-xmark"></i>`;
                    
                    pill.querySelector("i").addEventListener("click", (e) => {
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

            // Sync with native select for accurate form fallback data
            if (nativeSelect) {
                Array.from(nativeSelect.options).forEach(nativeOpt => {
                    const correspondingCheckbox = Array.from(options).find(cb => cb.value === nativeOpt.value);
                    if (correspondingCheckbox) {
                        nativeOpt.selected = correspondingCheckbox.checked;
                    }
                });
            }
        };

        options.forEach(opt => opt.addEventListener("change", updatePills));

        if (selectAllBtn) {
            selectAllBtn.addEventListener("change", (e) => {
                const isChecked = e.target.checked;
                options.forEach(opt => opt.checked = isChecked);
                updatePills();
            });
        }

        updatePills();
    });
}

function performBlogSearch() {
	const searchInput = document.getElementById("search-input");
	const params = new URLSearchParams();

	// Add search query
	const searchQuery = searchInput?.value.trim();
	if (searchQuery) {
		params.append("search", searchQuery);
	}

	// Add sort
	const sortSelect = document.getElementById("sort-select");
	const sortValue = sortSelect?.value;
	if (sortValue && sortValue !== "newest") {
		params.append("sort", sortValue);
	}

	// Add category
	const categorySelect = document.getElementById("category-select");
	const categoryValue = categorySelect?.value;
	if (categoryValue && categoryValue !== "All Topics") {
		params.append("category", categoryValue);
	}

	// Add tags
	const tagInput = document.getElementById("tags-input");
	const tagValue = tagInput?.value.trim();
	if (tagValue) {
		params.append("tags", tagValue);
	}

	// Add date range
	const startDate = document.getElementById("start-date");
	const endDate = document.getElementById("end-date");
	if (startDate?.value) {
		params.append("start_date", startDate.value);
	}
	if (endDate?.value) {
		params.append("end_date", endDate.value);
	}

	// Add reading time filter
	const readingTimeCheckboxes = Array.from(document.querySelectorAll('#reading-time-multiselect .multiselect-options input[type="checkbox"]'));
	const checkedReadingTime = readingTimeCheckboxes
		.filter(cb => cb.checked)
		.map(cb => cb.value)
		.join(",");
	if (checkedReadingTime) {
		params.append("reading_time", checkedReadingTime);
	}

	// Add type filter
	const typeCheckboxes = Array.from(document.querySelectorAll('#type-multiselect .multiselect-options input[type="checkbox"]'));
	const checkedTypes = typeCheckboxes
		.filter(cb => cb.checked)
		.map(cb => cb.value)
		.join(",");
	if (checkedTypes) {
		params.append("type", checkedTypes);
	}

	// Navigate with parameters
	const queryString = params.toString();
	const url = queryString ? `/blog?${queryString}` : "/blog";
	location.href = url;
}

function restoreFilterState() {
	const params = new URLSearchParams(location.search);

	// Restore search input
	const searchInput = document.getElementById("search-input");
	const searchParam = params.get("search");
	if (searchInput && searchParam) {
		searchInput.value = searchParam;
	}

	// Restore sort
	const sortSelect = document.getElementById("sort-select");
	const sortParam = params.get("sort");
	if (sortSelect && sortParam) {
		sortSelect.value = sortParam;
	}

	// Restore category
	const categorySelect = document.getElementById("category-select");
	const categoryParam = params.get("category");
	if (categorySelect && categoryParam) {
		categorySelect.value = categoryParam;
	}

	// Restore tags
	const tagInput = document.getElementById("tags-input");
	const tagsParam = params.get("tags");
	if (tagInput && tagsParam) {
		tagInput.value = tagsParam;
	}

	// Restore date range
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

	// Restore reading time checkboxes
	const readingTimeParam = params.get("reading_time");
	if (readingTimeParam) {
		const readingTimeValues = readingTimeParam.split(",");
		const readingTimeCheckboxes = document.querySelectorAll('#reading-time-multiselect .multiselect-options input[type="checkbox"]');
		readingTimeCheckboxes.forEach(checkbox => {
			if (readingTimeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
	}

	// Restore type checkboxes
	const typeParam = params.get("type");
	if (typeParam) {
		const typeValues = typeParam.split(",");
		const typeCheckboxes = document.querySelectorAll('#type-multiselect .multiselect-options input[type="checkbox"]');
		typeCheckboxes.forEach(checkbox => {
			if (typeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
	}
}

function initBlogSearch() {
	const searchInput = document.getElementById("search-input");
	const searchIcon = document.querySelector(".search-icon");
	const clearBtn = document.querySelector(".clear-filters-btn");
	const applyBtn = document.querySelector(".apply-filters-btn");
	const loadMoreBtn = document.getElementById("load-more-btn");
    
	if (!searchInput) return;
    
	if (searchIcon) {
		searchIcon.addEventListener("click", () => {
			performBlogSearch();
		});
	}
    
	searchInput.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			performBlogSearch();
		}
	});
    
	if (applyBtn) {
		applyBtn.addEventListener("click", performBlogSearch);
	}
	if (clearBtn) {
		clearBtn.addEventListener("click", () => {
			if (searchInput) searchInput.value = "";
			const filterDrawer = document.getElementById("filter-drawer");
			if (filterDrawer) {
				filterDrawer.querySelectorAll('input[type="text"]').forEach(input => input.value = "");
				filterDrawer.querySelectorAll('input[type="date"]').forEach(input => input.value = "");
				filterDrawer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);
				filterDrawer.querySelectorAll('select').forEach(select => select.value = select.options[0].value);
			}
			location.href = "/blog";
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
            
			location.href = `/blog?${params.toString()}`;
		});
	}
    
	restoreFilterState();
    initMultiselects();
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", () => {
		initBlogSearch();
	});
} else {
	initBlogSearch();
}