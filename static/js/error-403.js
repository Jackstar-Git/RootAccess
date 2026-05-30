document.addEventListener('DOMContentLoaded', function(){
    const msg = window.errorMessage || 'Access denied';
    if (window.notify) {
        notify(msg, 'error');
    } else if (window.showToast) {
        showToast(msg, 'error');
    }
});
