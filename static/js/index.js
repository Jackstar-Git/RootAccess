function initHeroTilt() {
    const wrapper = document.querySelector(".hero-3d-wrapper");
    if (!wrapper) return;

    document.addEventListener("mousemove", (e) => {
        let xAxis = (window.innerWidth / 2 - e.pageX) / 25;
        let yAxis = (window.innerHeight / 2 - e.pageY) / 25;
        wrapper.style.transform = `rotateY(${-xAxis}deg) rotateX(${yAxis}deg)`;
    });

    document.addEventListener("mouseleave", () => {
        wrapper.style.transform = `rotateY(0deg) rotateX(0deg)`;
        wrapper.style.transition = "all 0.5s ease";
    });

    document.addEventListener("mouseenter", () => {
        wrapper.style.transition = "none";
    });
}

initHeroTilt();

function calculateDaysSinceStart() {
    const startDate = new Date("2021-07-25");
    const currentDate = new Date();
    const timeDiff = currentDate - startDate;
    const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    return daysDiff;
}

function roundDownToHalfYear(days) {
    const daysInHalfYear = 182.5;
    return Math.floor(days / daysInHalfYear) * 0.5;
}

const daysPassed = calculateDaysSinceStart();
const halfYears = roundDownToHalfYear(daysPassed);

document.getElementById("years-of-experience").textContent = `${halfYears}+`;


function startAccidentalRecursion(count = 0) {
    const element = document.getElementById("accidental-recursions");
    if (!element) return;

    element.textContent = count.toLocaleString();
    const jitter = Math.floor(Math.random() * 100) + 500;
    
    setTimeout(() => {
        startAccidentalRecursion(count + 1);
    }, jitter);
}

startAccidentalRecursion();


function triggerTypeErrorGlitch() {
    const errorEl = document.getElementById("type-error-stat");
    const errors = ["null", "undefined", "NaN", "[object Object]", "404", "Error", "TypeError", "AttributeError", "ReferenceError"];
    
    setInterval(() => {
        const randomError = errors[Math.floor(Math.random() * errors.length)];
        errorEl.textContent = randomError;
        
        setTimeout(() => {
            errorEl.style.color = ""; 
        }, 150);
    }, 3000); 
}
triggerTypeErrorGlitch();
