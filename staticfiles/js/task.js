function showPopup() {
    const popup = document.getElementById('popup');
    
    // Show the popup by adding the 'show' class
    popup.classList.add('show');
    
    // After 5 seconds, fade it out by removing the 'show' class
    setTimeout(() => {
      popup.classList.remove('show');
    }, 5000); // 5 seconds
  }
  
  // Trigger the popup to show after the page loads
  window.onload = function() {
    showPopup();
  };

