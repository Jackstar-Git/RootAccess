function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    const monthNames = ["Jänner", "Februar", "März", "April", "Mai", "Juni",
      "Juli", "August", "September", "Oktober", "November", "Dezember"];
    var currentMonth = currentDate.getMonth();
    document.querySelector("#displayYear").innerHTML = "" + monthNames[currentMonth] + " " + currentYear;
}
  
getYear();

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

if (!getCookie("cookiesAccepted")) {
  document.getElementById("privacy-notice").style.display = "flex";
}

// Add event listener to accept button
document.getElementById("acceptCookies").addEventListener("click", function() {
  document.getElementById("privacy-notice").style.transform = "translateY(100%)";
  document.cookie = "cookiesAccepted=true; path=/; max-age=" + 60 * 60 * 24 * 365;
});