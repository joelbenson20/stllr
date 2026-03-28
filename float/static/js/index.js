const vote_buttons = document.querySelectorAll('.vote-button');

vote_buttons.forEach(button => {
    button.addEventListener('click', (e) => {

        e.preventDefault();
        const webpageId = button.dataset.webpageId;
        const voteType = button.dataset.voteType;

        fetch(`/api/vote/webpage/${webpageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({ vote_type: voteType })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response received:', data);
        })
        .catch(error => console.error('Error:', error));
    });
});