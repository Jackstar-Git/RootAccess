async function deletePost(blogId) {
    if (!confirm("Are you sure you want to delete this post permanently?")) return;

    try {
        const response = await fetch(`/api/delete-blog`, {
            credentials: "same-origin",
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.getElementById('csrf_token').value
            },
            body: JSON.stringify({ id: blogId })
        });

        const result = await response.json();
        if (result.success) {
            window.location.href = "/admin/blogs/all";
        } else {
            notify(result.error || 'Error', 'error');
        }
    } catch (err) {
        notify('Failed to communicate with the server.', 'error');
    }
}