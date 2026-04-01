document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("adminSidebar");
    const toggleBtn = document.getElementById("toggleBtn");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const menuToggles = document.querySelectorAll(".menu-toggle");

    if (!sidebar) return; // Guard against missing sidebar

    const savedState = localStorage.getItem("sidebar-collapsed");
    if (savedState === "true") {
        sidebar.classList.add("collapsed");
    }

    // Toggle sidebar (desktop collapse or mobile drawer)
    const toggleSidebar = () => {
        sidebar.classList.toggle("collapsed");
        const isCollapsed = sidebar.classList.contains("collapsed");
        localStorage.setItem("sidebar-collapsed", isCollapsed);

        if (isCollapsed) {
            document.querySelectorAll(".submenu").forEach(sub => {
                sub.style.display = "none";
            });
            document.querySelectorAll(".menu-toggle").forEach(toggle => {
                toggle.classList.remove("active");
            });
        }
    };

    // Desktop collapse button
    if (toggleBtn) {
        toggleBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    // Mobile menu button handler - toggle sidebar drawer
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    // Close sidebar when clicking on a nav link (mobile)
    const navLinks = document.querySelectorAll(".nav-item > a:not(.menu-toggle)");
    navLinks.forEach(link => {
        link.addEventListener("click", () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.add("collapsed");
                localStorage.setItem("sidebar-collapsed", "true");
            }
        });
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener("click", (e) => {
        if (window.innerWidth <= 768) {
            const isSidebarClick = sidebar && sidebar.contains(e.target);
            const isButtonClick = mobileMenuBtn && mobileMenuBtn.contains(e.target);
            
            if (!isSidebarClick && !isButtonClick && !sidebar.classList.contains("collapsed")) {
                sidebar.classList.add("collapsed");
                localStorage.setItem("sidebar-collapsed", "true");
            }
        }
    });

    // Close sidebar on escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && window.innerWidth <= 768 && !sidebar.classList.contains("collapsed")) {
            sidebar.classList.add("collapsed");
            localStorage.setItem("sidebar-collapsed", "true");
        }
    });

    // Menu toggle dropdowns
    menuToggles.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            
            if (sidebar.classList.contains("collapsed")) {
                sidebar.classList.remove("collapsed");
                localStorage.setItem("sidebar-collapsed", "false");
            }

            const submenu = btn.nextElementSibling;
            if (!submenu) return;

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
});