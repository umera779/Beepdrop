document.getElementById('refresh-balance').addEventListener('click', function() {
    // Fetch the updated balance via AJAX
    fetch('/api/balance/')
        .then(response => response.json())
        .then(data => {
            if (data.balance !== undefined) {
                // Update the balance in the DOM
                document.getElementById('counter-value').textContent = data.balance;
            } else {
                console.error('Balance not found in response.');
            }
        })
        .catch(error => {
            console.error('Error fetching balance:', error);
        });
});