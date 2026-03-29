const float_buttons = document.querySelectorAll('.float-button');

float_buttons.forEach(button => {
    button.addEventListener('click', (e) => {

        const webpage_id = button.dataset.webpageId;
        updateFloatButton(button);

        fetch(`/api/vote/webpage/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({ webpage_id: webpage_id })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response received:', data);
        })
        .catch(error => console.error('Error:', error));
    });
});

function updateFloatButton(button) {
    //Toggle the data-voted attribute
    if (button.dataset.voted === 'true') {
        button.dataset.voted = 'false';
    }
        else {
        button.dataset.voted = 'true';
    }

    //Update float count
    let floatCount = button.closest('p').querySelector('.float-count');
    let count = parseInt(floatCount.textContent);
    if (button.dataset.voted === 'true') {
        count += 1;
    } else {
        count -= 1;
    }
    floatCount.textContent = count;
}