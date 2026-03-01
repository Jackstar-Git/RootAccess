async function loadCaptcha() {
    const csrfToken = document.getElementById('csrf_token').value;
    const captchaImg = document.getElementById("captcha-img");

    try {
        const response = await fetch('/api/generate-captcha', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': csrfToken
            }
        });

        if (!response.ok) {
            throw new Error('Failed to reload captcha');
        }

        const jsonResponse = await response.json();
        const b64Response = jsonResponse.captcha;

        captchaImg.alt = "Captcha Image";
        captchaImg.src = b64Response;


    } catch (error) {
        console.error('Error reloading captcha:', error);
    }
}