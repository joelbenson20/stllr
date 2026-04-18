const forms = document.querySelectorAll('.comment-form');
forms.forEach(form => {
    form.addEventListener('submit', (e) => {
        e.preventDefault()
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
    })
})


const commentVoteUrl = '/comments/vote/'
const commentVoteButtons = document.querySelectorAll('a.comment-vote-button')

commentVoteButtons.forEach(voteButton => {
    voteButton.addEventListener('click', function(e) {
        e.preventDefault();
        var formData = new FormData()
        formData.append('id', voteButton.dataset.id)
        formData.append('action', voteButton.dataset.action)
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': voteButton.dataset.csrfToken},
            mode: 'same-origin',
            body: formData
        }
        fetch(commentVoteUrl, options)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data['status'] === '200') {
                var previousAction = voteButton.dataset.action;
                var newAction = previousAction === 'vote' ? 'unvote' : 'vote';
                voteButton.dataset.action = newAction

                var voteCount = voteButton.querySelector('.vote-count');
                var previousCount = parseInt(voteCount.textContent);
                voteCount.textContent = previousAction === 'vote' ? previousCount + 1 : previousCount - 1;

                var icon = voteButton.querySelector('i');
                icon.classList.toggle('bi-star-fill')
                icon.classList.toggle('bi-star');
            }
        })
    })
})