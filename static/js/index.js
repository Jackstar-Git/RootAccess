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
