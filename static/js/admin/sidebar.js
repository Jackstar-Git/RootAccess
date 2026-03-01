// Submenu Toggle
const toggles = document.querySelectorAll(".menu-toggle");
toggles.forEach(toggle => {
    toggle.addEventListener("click", function(event) {
        event.preventDefault();
        this.classList.toggle("submenu-open");
        const submenu = this.nextElementSibling;
        submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    });
});