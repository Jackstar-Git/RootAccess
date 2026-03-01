function filterProducts() {
    const category = document.getElementById("category-filter").value.trim();
    const newUrl = new URL(window.location.href);

    if (category === "all") {
        newUrl.searchParams.delete("category");
    }
    else { 
        newUrl.searchParams.set("category", category);
    }
    window.location.href = newUrl.toString();
}

// Function to sort products based on selected sorting option
function searchProducts() {
    const query = document.getElementById("search-input").value.trim();
    const newUrl = new URL(window.location.href);


    if (query === "") {
        newUrl.search.delete("search");
    }
    else {
        newUrl.searchParams.set("search", query);
    }
    window.location.href = newUrl.toString();
}


function sortProducts() {
    let sortValue = document.getElementById("sort-options").value;
    let container = document.getElementById("products-container");
    let products = Array.from(container.getElementsByClassName("product"));

    let sortedProducts = products.sort(function(a, b) {
        let priceA = parseFloat(a.getAttribute("data-price"));
        let priceB = parseFloat(b.getAttribute("data-price"));
        let nameA = a.getAttribute("data-name").toLowerCase();
        let nameB = b.getAttribute("data-name").toLowerCase();

        switch (sortValue) {
            case "price-asc":
                return priceA - priceB;
            case "price-desc":
                return priceB - priceA;
            case "name-asc":
                return nameA.localeCompare(nameB);
            case "name-desc":
                return nameB.localeCompare(nameA);
            default:
                return 0;
        }
    });

    sortedProducts.forEach(function(product) {
        container.appendChild(product);
    });
}

async function calculateCart(csrfToken) {

    try {
        const response = await fetch('/api/calculate-cart', {
            method: 'GET',
            headers: {
                'X-CSRF-Token': csrfToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to calculate cart');
        }

        return await response.json();
    } catch (error) {
        console.error('Error calculating cart:', error);
        return null;
    }
}


async function addToCart(productId) {
    const csrfToken = document.getElementById('csrf_token').value;
    const data = {
        product_id: productId,
        quantity: 1
    };

    try {
        const response = await fetch('/api/update-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            await calculateCart(csrfToken);
            window.location.reload();
        } else {
            const errorMessage = await response.text();
            console.error(errorMessage); 
        }
    } catch (error) {
        console.error(error)
    }
}