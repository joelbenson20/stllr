const postUrl = 'http://127.0.0.1/comments/post/'
const forms = document.querySelectorAll('.comment-form');

forms.forEach(form => {
    form.addEventListener('submit', (event => {
        event.preventDefault()
        const formData = new FormData(form);
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': formData.get('csrfToken')},
            body: formData
        }
        fetch(form.action, options)
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
    }))
})