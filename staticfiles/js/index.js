
$(document).ready(function () {
    const button = $('#mine-btn-js');
    const disableDuration = 4 * 60 * 60 * 1000; // 4 hours in milliseconds

    // Function to disable the button with a countdown
    function disableButton(remainingTime) {
        button.prop('disabled', true); // Disable the button
        const endTime = Date.now() + remainingTime;

        const interval = setInterval(() => {
            const now = Date.now();
            const timeLeft = endTime - now;

            if (timeLeft <= 0) {
                clearInterval(interval); // Clear the interval
                button.prop('disabled', false); // Enable the button
                button.text('Start Mining Keys!'); // Reset button text
            } else {
                // Calculate hours, minutes, and seconds
                const hours = Math.floor(timeLeft / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                button.text(`${hours}:${minutes}:${seconds}`); // Update the button text with countdown
            }
        }, 1000); // Update every second
    }

    // Fetch button state on page load
    $.ajax({
        url: '/get-button-state/', // Replace with the endpoint to fetch button state
        type: 'GET',
        success: function (response) {
            if (response.state === 'clicked') {
                // If the button is already clicked, disable it with the remaining time
                disableButton(response.remaining_time);
            }
        },
        error: function () {
            console.error('Failed to fetch button state');
        }
    });

    // Handle button click
    button.click(function () {
        $.ajax({
            url: '/update-button-state/', // Replace with the endpoint to update button state
            type: 'POST',
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val() // Include CSRF token
            },
            success: function () {
                // On successful state update, disable the button for the full duration
                disableButton(disableDuration);
            },
            error: function () {
                console.error('Failed to update button state');
            }
        });
    });

    // Handle form submission via AJAX to update the counter
    $('#counter-form').submit(function (e) {
        e.preventDefault(); // Prevent the default form submission
        $.ajax({
            url: $(this).attr('action'), // URL to send the request
            type: 'POST', // Use POST method
            data: $(this).serialize(), // Serialize the form data
            success: function (response) {
                // Update the counter value in the HTML
                $('#counter-value').text(response.counter_value);

                // If the button state is 'clicked', start the countdown
                if (response.button_state === 'clicked') {
                    const remainingTime = disableDuration; // Set remaining time (4 hours)
                    localStorage.setItem('disabledUntil', Date.now() + remainingTime); // Save state
                    disableButton(remainingTime);
                }
            },
            error: function (xhr, errmsg, err) {
                alert("There was an error with the request: " + errmsg);
            }
        });
    });
});
