async function deletePost(blogId) {
    if (!confirm("Are you sure you want to delete this post permanently?")) return;

    try {
        const response = await fetch(`/api/delete-blog`, {
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
            alert("Error: " + result.error);
        }
    } catch (err) {
        alert("Failed to communicate with the server.");
    }
}