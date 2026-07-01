function initThemeSwitch() {
    const switches = document.querySelectorAll('.theme-switch');
    const root = document.documentElement;

    function applyMode(mode) {
        if (mode === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
        }

        switches.forEach((switchEl) => {
            const thumb = switchEl.querySelector('.switch-thumb');
            if (mode === 'dark') {
                switchEl.classList.add('dark');
                switchEl.setAttribute('aria-pressed', 'true');
                if (thumb) thumb.style.transform = 'translateX(26px)';
            } else {
                switchEl.classList.remove('dark');
                switchEl.setAttribute('aria-pressed', 'false');
                if (thumb) thumb.style.transform = 'translateX(0)';
            }
        });

        try {
            localStorage.setItem('theme', mode);
        } catch (e) {
            console.warn('Unable to persist theme preference:', e);
        }
    }

    function toggleTheme() {
        const current = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyMode(current);
    }

    const saved = localStorage.getItem('theme');
    const initial = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyMode(initial);

    switches.forEach((switchEl) => switchEl.addEventListener('click', toggleTheme));
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeSwitch);
} else {
    initThemeSwitch();
}
