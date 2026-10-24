const root = document.documentElement;
const builtins = ["light", "dark"];
const fallback = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
let stylesheet = document.getElementById("active-custom-theme");
let stylesheetTheme = null;
try {
    stylesheetTheme = stylesheet
        ? localStorage.getItem("active-theme")
        : null;
} catch {}

function setActiveTheme(themeId, persist = true) {
    if (!window.portfolioThemeIds.includes(themeId)) return false;

    if (builtins.includes(themeId)) {
        stylesheet?.remove();
        stylesheet = null;
        stylesheetTheme = null;
        root.dataset.theme = themeId;
    } else {
        root.dataset.theme = themeId;
        if (stylesheetTheme !== themeId) {
            stylesheet?.remove();
            stylesheet = document.createElement("link");
            stylesheet.rel = "stylesheet";
            stylesheet.id = "active-custom-theme";
            stylesheet.href = `/static/css/themes/${encodeURIComponent(themeId)}.css`;
            stylesheet.onerror = () => setActiveTheme(fallback);
            document.head.appendChild(stylesheet);
            stylesheetTheme = themeId;
        }
    }

    if (persist) {
        try {
            localStorage.setItem("active-theme", themeId);
        } catch {}
    }
    return true;
}

window.portfolioThemes = [
    { id: "light", name: "Light", color_schema: "light" },
    { id: "dark", name: "Dark", color_schema: "dark" },
];
window.portfolioThemeIds = builtins;
window.setActiveTheme = setActiveTheme;

fetch("/api/themes")
    .then(response => response.ok ? response.json() : Promise.reject(new Error("Theme list unavailable")))
    .then(payload => {
        window.portfolioThemes = Array.isArray(payload.themes) ? payload.themes : [];
        window.portfolioThemeIds = window.portfolioThemes.map(theme => theme.id);
        let selected = stylesheetTheme;
        try {
            selected ||= localStorage.getItem("active-theme");
        } catch {}
        selected ||= root.dataset.theme;
        if (!setActiveTheme(selected, false)) setActiveTheme(fallback, false);
    })
    .catch(() => setActiveTheme(fallback, false));