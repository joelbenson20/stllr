function initPostCardLink(card) {
    card.addEventListener('click', e => {
        if (!e.target.closest('a, button, form')) {
            window.location.href = card.dataset.postUrl;
        }
    });
}

function initPostForm(form) {
    initFormSubmission(form);
    const replyFormContainer = form.closest('.reply-form-container');
    if (replyFormContainer) initReplyAutoFocus(replyFormContainer);
    initMarkdownToggle(form);
}

function initMarkdownToggle(form) {
    const textarea = form.querySelector('.post-form-textarea');
    const previewContainer = form.querySelector('.post-form-markdown-preview-container');
    const previewButton = form.querySelector('.post-form-markdown-preview-button');
    const editButton = form.querySelector('.post-form-markdown-edit-button');

    previewButton.addEventListener('click', () => {
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append('content', textarea.value);
        fetch(new URL(previewButton.dataset.endpoint, document.baseURI).href, {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            body: formData
        })
        .then(r => r.json())
        .then(response => {
            if (response.status === '200') {
                previewContainer.innerHTML = response.markdown;
                previewContainer.style.display = 'block';
                previewButton.style.display = 'none';
                editButton.style.display = 'block';
                textarea.style.display = 'none';
            }
        });
    });

    editButton.addEventListener('click', (e) => {
        e.preventDefault();
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
        previewButton.style.display = 'block';
        editButton.style.display = 'none';
        textarea.style.display = 'block';
        const end = textarea.value.length;
        textarea.focus();
        textarea.setSelectionRange(end, end);
    });
}

function initFormSubmission(form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        var formData = new FormData(form);
        var csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            body: formData
        }
        fetch(form.action, options)
        .then(response => response.json())
        .then(response => {
            if (response.status === '201') {
                var postTree = document.querySelector('#postFeed');
                var parentId = form.querySelector('[name=parent]').value
                if (parentId) {
                    postTree = document.querySelector(`#children${parentId}`);
                }
                postTree.insertAdjacentHTML('afterbegin', response.post);

                // Initialize new reply form
                var newPost = document.querySelector(`#post${response.postId}`);
                var newStarButton = newPost.querySelector('.post-star-button');
                var newForm = newPost.querySelector('.post-form')
                initPostStarButton(newStarButton);
                initPostForm(newForm);
                initPostCardLink(newPost); // Done by Claude, requires review

                // Close form container for threaded posts
                if (parentId) {
                    var parentFormContainer = document.querySelector(`#reply-form-container-${parentId}`);
                    parentFormContainer.classList.remove('show');
                    // Done by Claude, requires review
                    var replyCountSpan = document.querySelector(`#post${parentId} .post-replies-button span`);
                    if (replyCountSpan) replyCountSpan.textContent = parseInt(replyCountSpan.textContent) + 1;
                }

                // Reset and close the form
                form.reset();
                var cancelButton = form.querySelector('.post-cancel-button');
            }
        })
        .catch(error => console.error('Error:', error))
    })
    
}

function initPostStarButton(button) {
    button.addEventListener('click', (e) => {
            e.preventDefault();
            var formData = new FormData()
            formData.append('id', button.dataset.id)
            formData.append('action', button.dataset.action)
            var options = {
                method: 'POST',
                headers: {'X-CSRFToken': button.dataset.csrfToken},
                mode: 'same-origin',
                body: formData
            }
            fetch(new URL(button.dataset.endpoint, document.baseURI).href, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === '200') {
                    var previousAction = button.dataset.action;
                    var newAction = previousAction === 'star' ? 'unstar' : 'star';
                    button.dataset.action = newAction

                    var starCount = button.querySelector('.star-count');
                    var previousCount = parseInt(starCount.textContent);
                    starCount.textContent = previousAction === 'star' ? previousCount + 1 : previousCount - 1;

                    var icon = button.querySelector('i');
                    icon.classList.toggle('bi-star-fill')
                    icon.classList.toggle('bi-star');
                }
            })
        })
}

function initReplyAutoFocus(replyFormContainer) {
    replyFormContainer.addEventListener('shown.bs.collapse', function () {
        this.querySelector('textarea').focus();
    })
}

function initForum() {

    // Initialize star buttons
    var postStarButtons = document.querySelectorAll('.post-star-button');
    postStarButtons.forEach(button => {
        initPostStarButton(button);
    })

    // Initialize post forms
    var postForms = document.querySelectorAll('.post-form');
    postForms.forEach(form => {
        initPostForm(form)
    })

    // Focus in root form
    var rootPostForm = document.querySelectorAll('.post-form')[0];
    rootPostForm.querySelector('textarea').focus();

    // Init post card links
    document.querySelectorAll('.post[data-post-url]').forEach(initPostCardLink);

}

initForum();
