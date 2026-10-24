(() => {
    const root = document.documentElement;
    const fallback = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    let theme = fallback;

    try {
        theme = localStorage.getItem("active-theme") || fallback;
    } catch {}
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(theme)) theme = fallback;

    root.dataset.theme = theme;
    if (theme === "light" || theme === "dark") return;

    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.id = "active-custom-theme";
    stylesheet.href = `/static/css/themes/${theme}.css`;
    document.head.appendChild(stylesheet);
})();