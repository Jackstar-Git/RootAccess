function loadTheme() {
    try {
        const saved = localStorage.getItem("active-theme");
        if (saved) {
            document.documentElement.setAttribute("data-theme", saved);
        } else {
            const initial = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", initial);
        }
    } catch (e) {}
};
loadTheme();