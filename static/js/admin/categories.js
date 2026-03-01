document.getElementById("add-btn").addEventListener("click", function () {
    const inputList = document.querySelector(".categories-wrapper");
    const wrapper = document.createElement("div");
    wrapper.classList.add("category-item");

    wrapper.innerHTML = `
        <input type="text" name="category" placeholder="Name der neuen Kategorie eingeben" required>
            <div class="category-actions">
                <a class="btn delete-btn"><i class="fas fa-trash-alt"></i></a>
            </div>`;
    inputList.appendChild(wrapper);
});

document.querySelector(".categories-list").addEventListener("click", function (event) {
    const deleteButton = event.target.closest(".delete-btn");

    if (deleteButton) {
        const wrapper = deleteButton.closest(".category-item");
        if (wrapper) {
            wrapper.remove();
        }
    }
});