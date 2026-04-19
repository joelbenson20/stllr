// Override comment form submissions for asynchronous processing
document.addEventListener('submit', (e) => {
    if (!e.target.classList.contains('comment-form')) return;
    
    e.preventDefault();
    const form = e.target;
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData(form);
    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken},
        body: formData
    }
    fetch(form.action, options)
    .then(response => response.json())
    .then(response => {
        if (response.status === '201') {
            var parentId = form.dataset.parentId;

            // Insert new comment
            var commentTree = document.querySelector('#comment-tree');
            if (parentId) {
                commentTree = document.querySelector(`#children-${parentId}`);
            }
            commentTree.insertAdjacentHTML('afterbegin', response.comment);  

            // Close form container for threaded comments
            if (parentId) {
                var formContainer = document.querySelector(`#comment-form-container-${parentId}`);
                var formContainerCollapse = bootstrap.Collapse.getOrCreateInstance(formContainer);
                formContainerCollapse.hide();
            }

            // Reset the form
            form.reset();
        }
    })
    .catch(error => console.error('Error:', error))
})


const commentVoteUrl = '/comments/vote/'
const commentVoteButtons = document.querySelectorAll('a.comment-vote-button')

// Override comment votes for asyncronous processing.
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