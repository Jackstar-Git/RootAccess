(function () {
    function syncNativeSelect(multiselect, nativeSelect, options) {
        if (!nativeSelect) return;

        Array.from(nativeSelect.options).forEach((nativeOption) => {
            const correspondingCheckbox = Array.from(options).find((checkbox) => checkbox.value === nativeOption.value);
            if (correspondingCheckbox) {
                nativeOption.selected = correspondingCheckbox.checked;
            }
        });
    }

    function updateMultiselectPills(multiselect) {
        const header = multiselect.querySelector(".multiselect-header");
        const searchInput = multiselect.querySelector(".multiselect-search");
        const pillsContainer = multiselect.querySelector(".multiselect-pills");
        const checkboxes = multiselect.querySelectorAll('.multiselect-options input[type="checkbox"]');
        const selectAllBtn = multiselect.querySelector(".select-all");
        const nativeSelect = multiselect.previousElementSibling;

        pillsContainer.innerHTML = "";
        let allChecked = true;

        checkboxes.forEach((checkbox) => {
            if (!checkbox.checked) {
                allChecked = false;
                return;
            }

            const label = checkbox.closest(".filter-list-item");
            const labelText = label?.querySelector("span")?.textContent?.trim() || checkbox.value;
            const pill = document.createElement("span");
            pill.className = "multiselect-pill";
            pill.innerHTML = `${labelText} <i class="fa-solid fa-xmark"></i>`;

            const dismissIcon = pill.querySelector("i");
            dismissIcon.addEventListener("click", (event) => {
                event.stopPropagation();
                checkbox.checked = false;
                updateMultiselectPills(multiselect);
            });

            pillsContainer.appendChild(pill);
        });

        if (selectAllBtn) {
            selectAllBtn.checked = allChecked && checkboxes.length > 0;
        }

        searchInput.placeholder = multiselect.classList.contains("open") ? "Search..." : "";
        syncNativeSelect(multiselect, nativeSelect, checkboxes);
    }

    function initCustomMultiselects() {
        const multiselects = document.querySelectorAll(".custom-multiselect");

        multiselects.forEach((multiselect) => {
            if (multiselect.dataset.multiselectInitialized === "true") return;
            multiselect.dataset.multiselectInitialized = "true";

            const nativeSelect = multiselect.previousElementSibling;
            if (nativeSelect && nativeSelect.tagName === "SELECT") {
                nativeSelect.style.display = "none";
            }

            multiselect.style.display = "block";

            const header = multiselect.querySelector(".multiselect-header");
            const searchInput = multiselect.querySelector(".multiselect-search");
            const checkboxInputs = multiselect.querySelectorAll('.multiselect-options input[type="checkbox"]');
            const selectAllBtn = multiselect.querySelector(".select-all");
            const optionLabels = multiselect.querySelectorAll(".multiselect-options .filter-list-item");

            const toggleOpen = (isOpen) => {
                multiselect.classList.toggle("open", isOpen);
                if (isOpen) {
                    searchInput.focus();
                }
                searchInput.placeholder = isOpen ? "Search..." : "";
            };

            header.addEventListener("click", (event) => {
                if (event.target.closest(".multiselect-pill") || event.target.closest(".multiselect-pill i")) {
                    return;
                }

                if (event.target === searchInput || searchInput.contains(event.target)) {
                    toggleOpen(true);
                    return;
                }

                toggleOpen(!multiselect.classList.contains("open"));
            });

            document.addEventListener("click", (event) => {
                if (!multiselect.contains(event.target)) {
                    multiselect.classList.remove("open");
                    searchInput.placeholder = "";
                }
            });

            searchInput.addEventListener("input", (event) => {
                const term = event.target.value.trim().toLowerCase();
                multiselect.classList.add("open");
                searchInput.placeholder = "Search...";

                optionLabels.forEach((label) => {
                    const text = label.textContent.toLowerCase();
                    label.style.display = text.includes(term) ? "flex" : "none";
                });
            });

            checkboxInputs.forEach((checkbox) => {
                checkbox.addEventListener("change", () => updateMultiselectPills(multiselect));
            });

            if (selectAllBtn) {
                selectAllBtn.addEventListener("change", (event) => {
                    checkboxInputs.forEach((checkbox) => {
                        checkbox.checked = event.target.checked;
                    });
                    updateMultiselectPills(multiselect);
                });
            }

            updateMultiselectPills(multiselect);
        });
    }

    window.initCustomMultiselects = initCustomMultiselects;
})();
