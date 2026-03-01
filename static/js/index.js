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
