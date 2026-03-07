document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("adminSidebar");
    const toggleBtn = document.getElementById("toggleBtn");
    const menuToggles = document.querySelectorAll(".menu-toggle");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            
            if (sidebar.classList.contains("collapsed")) {
                document.querySelectorAll(".submenu").forEach(sub => {
                    sub.style.display = "none";
                });
                document.querySelectorAll(".menu-toggle").forEach(toggle => {
                    toggle.classList.remove("active");
                });
            }
        });
    }

    menuToggles.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            
            if (sidebar.classList.contains("collapsed")) {
                sidebar.classList.remove("collapsed");
                localStorage.setItem("sidebar-collapsed", "false");
            }

            const submenu = btn.nextElementSibling;
            
            const isHidden = !submenu.style.display || submenu.style.display === "none";

            if (isHidden) {
                submenu.style.display = "flex";
                btn.classList.add("active");
            } else {
                submenu.style.display = "none";
                btn.classList.remove("active");
            }
        });
    });

    const savedState = localStorage.getItem("sidebar-collapsed");
    if (savedState === "true") {
        sidebar.classList.add("collapsed");
    }

    toggleBtn?.addEventListener("click", () => {
        localStorage.setItem("sidebar-collapsed", sidebar.classList.contains("collapsed"));
    });
});