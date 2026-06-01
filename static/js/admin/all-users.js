async function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete the user '${username}' permanently?`)) return;

    try {
        const response = await fetch(`/api/delete-user`, {
            credentials: "same-origin",
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.getElementById('csrf_token').value
            },
            body: JSON.stringify({ username: username })
        });

        const result = await response.json();
        if (result.success) {
            window.location.href = "/admin/users/all";
        } else {
            notify(result.error || 'Error', 'error');
        }
    } catch (err) {
        notify('Failed to communicate with the server.', 'error');
    }
}

function updateSort() {
    const sortSelect = document.getElementById('sort-options');
    const sortValue = sortSelect.value;
    const hierarchyValue = document.getElementById('hierarchy-filter').value;
    const searchValue = document.getElementById('search-input').value;
    let url = '/admin/users/all?';
    if (sortValue) url += `sort=${sortValue}&`;
    if (hierarchyValue && hierarchyValue !== 'all') url += `hierarchy=${hierarchyValue}&`;
    if (searchValue) url += `search=${searchValue}&`;
    window.location.href = url.slice(0, -1); // Remove trailing '&'
}

// Helper function to update URL with hierarchy parameter
function updateHierarchyFilter() {
    const hierarchyInput = document.getElementById('hierarchy-filter');
    const hierarchyValue = hierarchyInput.value;
    const sortValue = document.getElementById('sort-options').value;
    const searchValue = document.getElementById('search-input').value;
    let url = '/admin/users/all?';
    if (sortValue) url += `sort=${sortValue}&`;
    if (hierarchyValue && hierarchyValue !== 'all') url += `hierarchy=${hierarchyValue}&`;
    if (searchValue) url += `search=${searchValue}&`;
    window.location.href = url.slice(0, -1); // Remove trailing '&'
}