const float_buttons = document.querySelectorAll('.float-button');

float_buttons.forEach(button => {
    button.addEventListener('click', (e) => {

        e.preventDefault();
        const webpageId = button.dataset.webpageId;

        fetch(`/api/vote/webpage/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({ webpage_id: webpageId })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response received:', data);
        })
        .catch(error => console.error('Error:', error));
    });
});