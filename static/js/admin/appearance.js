function updatePreview() {
    const iframe = document.getElementById("preview-iframe");
    const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

    let styleElement = iframeDocument.getElementById("iframe-style");
    if (!styleElement) {
        styleElement = iframeDocument.createElement("style");
        styleElement.id = "iframe-style";
        iframeDocument.head.appendChild(styleElement);
    }

    const colorInputs = document.querySelectorAll('input[type="color"]');
    let cssContent = ":root {";
    
    colorInputs.forEach(input => {
        const colorName = input.name;
        const colorValue = input.value;
        cssContent += `--${colorName}: ${colorValue} !important; `;
    });
    
    cssContent += "}";
    styleElement.innerHTML = cssContent;
}

function openModal() {
    document.getElementById("preview-modal").style.display = "block";
    updatePreview();
}

function closeModal() {
    document.getElementById("preview-modal").style.display = "none";
}


function hexToRgb(hex) {
    hex = hex.replace("#", "");
    return {
        r: parseInt(hex.substring(0, 2), 16),
        g: parseInt(hex.substring(2, 4), 16),
        b: parseInt(hex.substring(4, 6), 16)
    };
}

function rgbToLinear(rgb) {
    return [rgb.r, rgb.g, rgb.b].map(function(c) {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
}

function luminance(rgb) {
    const linear = rgbToLinear(rgb);
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(color1, color2) {
    const lum1 = luminance(hexToRgb(color1));
    const lum2 = luminance(hexToRgb(color2));
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
}

// Function to categorize the contrast ratio
function getContrastRating(ratio) {
    if (ratio >= 7) {
        return { rating: "Optimal", class: "excellent" };
    } else if (ratio >= 4.5) {
        return { rating: "Gut", class: "good" };
    } else if (ratio >= 3) {
        return { rating: "Ausreichend", class: "fair" };
    } else {
        return { rating: "Schlecht", class: "poor" };
    }
}

function updateContrastRatios() {
    const mainColor = document.getElementById("main-color").value;
    const secondaryColor = document.getElementById("secondary-color").value;
    const thirdColor = document.getElementById("third-color").value;
    const fontColor = document.getElementById("font-color").value;
    const secondaryFontColor = document.getElementById("secondary-font-color").value;
    const thirdFontColor = document.getElementById("third-font-color").value;
    const mainBgColor = document.getElementById("main-bg").value;
    const secondaryBgColor = document.getElementById("secondary-bg").value;
    const thirdBgColor = document.getElementById("third-bg").value;
    const warningColor = document.getElementById("warning-color").value;


    const combinations = [
        { font: fontColor, bg: mainBgColor, contrastId: "font1-main-bg-contrast", ratingId: "font1-main-bg-rating" },
        { font: fontColor, bg: secondaryBgColor, contrastId: "font1-secondary-bg-contrast", ratingId: "font1-secondary-bg-rating" },
        { font: fontColor, bg: thirdBgColor, contrastId: "font1-third-bg-contrast", ratingId: "font1-third-bg-rating" },
        { font: secondaryFontColor, bg: mainBgColor, contrastId: "font2-main-bg-contrast", ratingId: "font2-main-bg-rating" },
        { font: secondaryFontColor, bg: secondaryBgColor, contrastId: "font2-secondary-bg-contrast", ratingId: "font2-secondary-bg-rating" },
        { font: secondaryFontColor, bg: thirdBgColor, contrastId: "font2-third-bg-contrast", ratingId: "font2-third-bg-rating" },
        { font: thirdFontColor, bg: mainBgColor, contrastId: "font3-main-bg-contrast", ratingId: "font3-main-bg-rating" },
        { font: thirdFontColor, bg: secondaryBgColor, contrastId: "font3-secondary-bg-contrast", ratingId: "font3-secondary-bg-rating" },
        { font: thirdFontColor, bg: thirdBgColor, contrastId: "font3-third-bg-contrast", ratingId: "font3-third-bg-rating" },
        { font: mainColor, bg: mainBgColor, contrastId: "main-color-main-bg-contrast", ratingId: "main-color-main-bg-rating" },
        { font: mainColor, bg: secondaryBgColor, contrastId: "main-color-secondary-bg-contrast", ratingId: "main-color-secondary-bg-rating" },
        { font: mainColor, bg: thirdBgColor, contrastId: "main-color-third-bg-contrast", ratingId: "main-color-third-bg-rating" },
        { font: secondaryColor, bg: mainBgColor, contrastId: "secondary-color-main-bg-contrast", ratingId: "secondary-color-main-bg-rating" },
        { font: secondaryColor, bg: secondaryBgColor, contrastId: "secondary-color-secondary-bg-contrast", ratingId: "secondary-color-secondary-bg-rating" },
        { font: secondaryColor, bg: thirdBgColor, contrastId: "secondary-color-third-bg-contrast", ratingId: "secondary-color-third-bg-rating" },
        { font: fontColor, bg: warningColor, contrastId: "font1-warning-contrast", ratingId: "font1-warning-rating" },
        { font: warningColor, bg: mainBgColor, contrastId: "warning-main-bg-contrast", ratingId: "warning-main-bg-rating" }
    ];

    combinations.forEach(combination => {
        const ratio = contrastRatio(combination.font, combination.bg).toFixed(2);
        const rating = getContrastRating(ratio);
        document.getElementById(combination.contrastId).innerText = ratio;

        const ratingElement = document.getElementById(combination.ratingId);
        ratingElement.innerText = rating.rating;
        ratingElement.classList = rating.class;
    });
}

function resetColor(event) {
    let colorInput;
    if (event.target.tagName === "I") {
        colorInput = event.target.closest("button").previousElementSibling;
    } else if (event.target.tagName === "BUTTON") {
        colorInput = event.target.previousElementSibling;
    }
    colorInput.value = colorInput.dataset.original;
    updateContrastRatios();
}

updateContrastRatios();