const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';

const defaultHeaders = {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken
};

let currentEditIndex = null;

function editQuote(index, quote) {
    currentEditIndex = index;
    
    document.getElementById('editText').value = quote.text || '';
    document.getElementById('editAuthor').value = quote.author || '';
    document.getElementById('editOriginal').value = quote.original || '';
    
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    currentEditIndex = null;
}

async function submitEditForm(event) {
    event.preventDefault();
    
    if (currentEditIndex === null) {
        alert("Invalid operation.");
        return;
    }

    const text = document.getElementById('editText').value.trim();
    const author = document.getElementById('editAuthor').value.trim();
    const original = document.getElementById('editOriginal').value.trim() || null;

    if (!author) {
        alert("Author is required.");
        return;
    }

    try {
        const res = await fetch("/api/quotes", {
            method: "PUT",
            headers: defaultHeaders,
            body: JSON.stringify({
                index: currentEditIndex,
                text: text,
                author: author,
                original: original
            })
        });

        if (res.ok) {
            window.location.reload();
        } else {
            const errorData = await res.json();
            alert(`Error: ${errorData.error || 'Failed to update quote.'}`);
        }
    } catch (e) {
        console.error(e);
        alert("An error occurred while updating the quote.");
    }
}

async function deleteQuote(index) {
    // Get the quote item to display author in confirmation
    const quoteItem = document.querySelector(`.quote-item[data-index="${index}"]`);
    const authorElement = quoteItem?.querySelector('.quote-author');
    const author = authorElement?.textContent?.replace('— ', '') || 'this quote';

    if (confirm(`Are you sure you want to delete "${author}"?`)) {
        try {
            const res = await fetch("/api/quotes", {
                method: "DELETE",
                headers: defaultHeaders,
                body: JSON.stringify({ index: index })
            });

            if (res.ok) {
                window.location.reload();
            } else {
                const errorData = await res.json();
                alert(`Error: ${errorData.error || 'Failed to delete quote.'}`);
            }
        } catch (e) {
            console.error(e);
            alert("An error occurred while deleting the quote.");
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editModal');
    
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeEditModal();
        }
    });


    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && !modal.classList.contains('hidden')) {
            closeEditModal();
        }
    });
});
