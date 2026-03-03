document.querySelectorAll('.submenu-toggle').forEach(item => {
    item.addEventListener('click', event => {
        const parent = item.parentElement;
        parent.classList.toggle('open');
    });
});