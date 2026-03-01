async function updateCart(id, amount) {
    const csrfToken = document.getElementById("csrf_token").value;

    const data = {
        product_id: id,
        quantity: amount
    };

    await fetch("/api/update-cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken
        },
        body: JSON.stringify(data)
    })
    .catch(error => {
        console.error("Error updating cart:", error);
    });

    return calculateCart();
}

async function updateCartWithDOM(itemId, quantity) {
    const cartData = await updateCart(itemId, quantity);

    const productDiv = document.querySelector(`.product[data-product-id="${itemId}"]`);
    const quantityInput = productDiv.querySelector(".quantity_input");
    let currentQuantity = parseInt(quantityInput.value);
    let newQuantity = currentQuantity + quantity;

    if (quantity == 0 || newQuantity <= 0) {
        window.location.reload();
    }
    else {
        quantityInput.value = newQuantity;
    }

    if (cartData) {
        document.getElementById("discounted_subtotal").textContent = `€ ${cartData.total.toFixed(2)}`;
        document.getElementById("total_discount").textContent = `€ ${cartData.total_discount.toFixed(2)}`;
        document.getElementById("total_amount").textContent = `€ ${cartData.total.toFixed(2)}`;
        document.getElementById("subtotal").textContent = `€ ${cartData.old_total.toFixed(2)}`;
        document.getElementById("cart-tax").textContent = `€ ${cartData.tax.toFixed(2)}`;
    }

}

async function calculateCart() {
    const csrfToken = document.getElementById("csrf_token").value;

    try {
        const response = await fetch("/api/calculate-cart", {
            method: "GET",
            headers: {
                "X-CSRF-Token": csrfToken
            }
        });

        if (!response.ok) {
            throw new Error("Failed to calculate cart");
        }

        return await response.json();
    } catch (error) {
        console.error("Error calculating cart:", error);
        return null;
    }
}

async function checkDiscount() {
    const csrfToken = document.getElementById("csrf_token").value;
    const code = document.getElementById("discount-code");
    const errorField = document.getElementById("coupon-error");
    const discountInfoField = document.getElementById("discount-info");

    const data = {
        code: code.value
    };

    const response = await fetch("/api/check-discount", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const errorData = await response.json();
        errorField.innerHTML = errorData.error;
        return null;
    }

    const discountData = await response.json();
    code.value = "";

    const type = discountData.type === "absolute" ? "€" : "%";
    discountInfoField.innerHTML = `
        <button onclick="removeCoupon()" id="remove-discount" class="remove-discount-btn"><i class="fa-solid fa-trash"></i></button>
        <p><strong>${discountData.id}</strong> <span>${discountData.value.toFixed(2)} ${type}</span></p>
    `;
    errorField.innerHTML = "";

    const updatedCart = await calculateCart();

    if (updatedCart) {
        document.getElementById("discounted_subtotal").textContent = `€ ${updatedCart.total.toFixed(2)}`;
        document.getElementById("total_discount").textContent = `€ ${updatedCart.total_discount.toFixed(2)}`;
        document.getElementById("total_amount").textContent = `€ ${updatedCart.total.toFixed(2)}`;
        document.getElementById("subtotal").textContent = `€ ${updatedCart.old_total.toFixed(2)}`;
        document.getElementById("cart-tax").textContent = `€ ${updatedCart.tax.toFixed(2)}`;
    }
}
async function removeCoupon() {
    const csrfToken = document.getElementById("csrf_token").value;
    const code = document.getElementById("discount-code");
    const discountInfoField = document.getElementById("discount-info");
    const errorField = document.getElementById("coupon-error");

    const response = await fetch("/api/remove-discount", {
        method: "POST",
        headers: {
            "X-CSRF-Token": csrfToken
        }
    });

    if (!response.ok) {
        const errorData = await response.json();
        errorField.innerHTML = errorData.error;
        return null;
    }

    code.value = "";
    discountInfoField.innerHTML = "";
    errorField.innerHTML = "";

    const updatedCart = await calculateCart();

    if (updatedCart) {
        document.getElementById("discounted_subtotal").textContent = `€ ${updatedCart.total.toFixed(2)}`;
        document.getElementById("total_discount").textContent = `€ ${updatedCart.total_discount.toFixed(2)}`;
        document.getElementById("total_amount").textContent = `€ ${updatedCart.total.toFixed(2)}`;
        document.getElementById("subtotal").textContent = `€ ${updatedCart.old_total.toFixed(2)}`;
        document.getElementById("cart-tax").textContent = `€ ${updatedCart.tax.toFixed(2)}`;
    }
}



