// blog.js — page-specific blog behaviors

function performBlogSearch() {
	const filterDrawer = document.getElementById("filter-drawer");
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
	const readingTimeCheckboxes = Array.from(document.querySelectorAll("#reading-time-toggle ~ .filter-list-group input[type='checkbox']"));
	const checkedReadingTime = readingTimeCheckboxes
		.filter(cb => cb.checked)
		.map(cb => cb.value)
		.join(",");
	if (checkedReadingTime) {
		params.append("reading_time", checkedReadingTime);
	}

	// Add type filter
	const typeCheckboxes = Array.from(document.querySelectorAll("#type-toggle ~ .filter-list-group input[type='checkbox']"));
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
		const readingTimeCheckboxes = document.querySelectorAll("#reading-time-toggle ~ .filter-list-group input[type='checkbox']");
		readingTimeCheckboxes.forEach(checkbox => {
			if (readingTimeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
		// Expand the reading time section
		const readingTimeToggle = document.getElementById("reading-time-toggle");
		if (readingTimeToggle) readingTimeToggle.checked = true;
	}

	// Restore type checkboxes
	const typeParam = params.get("type");
	if (typeParam) {
		const typeValues = typeParam.split(",");
		const typeCheckboxes = document.querySelectorAll("#type-toggle ~ .filter-list-group input[type='checkbox']");
		typeCheckboxes.forEach(checkbox => {
			if (typeValues.includes(checkbox.value)) {
				checkbox.checked = true;
			}
		});
		// Expand the type section
		const typeToggle = document.getElementById("type-toggle");
		if (typeToggle) typeToggle.checked = true;
	}
}

function initBlogSearch() {
	const searchInput = document.getElementById("search-input");
	const searchIcon = document.querySelector(".search-icon");
	const clearBtn = document.querySelector(".clear-filters-btn");
	const applyBtn = document.querySelector(".apply-filters-btn");
	const loadMoreBtn = document.getElementById("load-more-btn");
    
	if (!searchInput) return;
    
	// Make search icon clickable and enter key functional
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
    
	// Handle apply filters button
	if (applyBtn) {
		applyBtn.addEventListener("click", performBlogSearch);
	}
    
	// Handle clear filters
	if (clearBtn) {
		clearBtn.addEventListener("click", () => {
			// Reset all inputs and navigate to /blog
			if (searchInput) searchInput.value = "";
			const filterDrawer = document.getElementById("filter-drawer");
			if (filterDrawer) {
				filterDrawer.querySelectorAll("input[type='text']").forEach(input => input.value = "");
				filterDrawer.querySelectorAll("input[type='date']").forEach(input => input.value = "");
				filterDrawer.querySelectorAll("input[type='checkbox']").forEach(checkbox => checkbox.checked = false);
				filterDrawer.querySelectorAll("select").forEach(select => select.value = select.options[0].value);
			}
			location.href = "/blog";
		});
	}
    
	// Handle load more button
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
    
	// Restore filter state from URL parameters
	restoreFilterState();
}

// ensure blog behaviours initialize only on blog pages
if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", () => {
		initBlogSearch();
	});
} else {
	initBlogSearch();
}
