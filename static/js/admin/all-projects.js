async function deleteProject(id) {
    if(!confirm('Are you sure you want to delete this project?')) return;
    
    try {
        const res = await fetch("/api/delete-project", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: id })
        });
        if(res.ok) {
            window.location.reload();
        } else {
            notify("Failed to delete project.", 'error');
        }
    } catch(e) { 
        console.error(e);
        notify("An error occurred while deleting the project.", 'error');
    }
}
