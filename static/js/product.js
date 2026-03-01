const imageContainer = document.getElementsByClassName("gallery-image");

const imageArray = Array.from(imageContainer);

imageArray.forEach(image => {
    image.addEventListener("click", function() {
        imageChange(this);
    });
});


function imageChange(clickedImage) {
    const displayImage = document.getElementById("main-image");
    displayImage.src = clickedImage.src; 
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

async function addToCart(event) {
    event.preventDefault();

    const form = document.getElementById('addToCartForm');
    const data = {
        product_id: form.querySelector('input[name="product_id"]').value,
        quantity: form.querySelector('input[name="quantity"]').value
    };
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;

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
