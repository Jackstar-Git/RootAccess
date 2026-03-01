function toggleUsesField() {
    const usesField = document.getElementById("uses_remaining");
    usesField.disabled = !usesField.disabled;
    if (usesField.disabled) usesField.value = "0";
}

function toggleValidityField() {
    const validField = document.getElementById("valid_till");
    validField.disabled = !validField.disabled;
    if (validField.disabled) validField.value = "";
}

function generateCode() {
    const idField = document.getElementById("id");
    const couponChars = []
    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let couponCode = "";

    for (let i = 0; i < 4; i++) {
        let segment = "";
        for (let j = 0; j < 4; j++) {
            const randomChar = characters.charAt(Math.floor(Math.random() * characters.length));
            segment += randomChar;
        }
        couponChars.push(segment);
    }

    couponCode = couponChars.join("-");
    idField.value = couponCode;
}