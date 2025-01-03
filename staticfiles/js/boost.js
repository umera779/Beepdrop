function showPopup() {
    const popup = document.getElementById('popup');
    if (popup) {
        popup.classList.add('show');
        setTimeout(() => {
            popup.classList.remove('show');
        }, 5000);
    }
}

// Trigger popup on load
window.onload = function () {
    showPopup();
};