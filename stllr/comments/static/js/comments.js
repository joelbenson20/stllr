const COMMENT_STAR_PATH = 'comments/star/';
const POST_COMMENT_PATH = 'comments/post/';
const MARKDOWNIFY_PATH = 'api/markdownify/';


function initCommentForm(form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            body: formData
        }
        fetch(BASE_URL + POST_COMMENT_PATH, options)
        .then(response => response.json())
        .then(response => {
            if (response.status === '201') {
                // In case of no parent, get the root comment tree (first one returned)
                var commentTree = document.querySelector('.comment-tree');
                // If comment parent, get the comment tree of the parent
                var parentId = form.querySelector('[name=parent]').value
                if (parentId) {
                    commentTree = document.querySelector(`#children-${parentId}`);
                }
                // Insert the new comment
                commentTree.insertAdjacentHTML('afterbegin', response.comment);

                // Initialize new reply form
                var newComment = document.querySelector(`#comment-${response.commentId}`)
                var newForm = newComment.querySelector('.comment-form');
                var newReplyFormContainer = newComment.querySelector('.reply-form-container');
                var newStarButton = newComment.querySelector('.comment-star-button');
                initCommentForm(newForm);
                initFormFocus(newForm);
                initReplyAutoFocus(newReplyFormContainer);
                initCommentStarButton(newStarButton);

                // Close form container for threaded comments
                if (parentId) {
                    var parentFormContainer = document.querySelector(`#reply-form-container-${parentId}`);
                    var parentFormContainerCollapse = bootstrap.Collapse.getOrCreateInstance(parentFormContainer);
                    parentFormContainerCollapse.hide();
                }

                // Reset and close the form
                form.reset();
                var cancelButton = form.querySelector('.comment-cancel-button');
                closeCommentForm(cancelButton);
            }
        })
        .catch(error => console.error('Error:', error))
    })
 }

 function initFormFocus(form) {
    var textarea = form.querySelector('.comment-form-textarea');
    textarea.addEventListener('focus', (e) => {
        var buttons = form.querySelector('.comment-form-buttons');
        if (textarea.offsetHeight < 100) {
            textarea.style.height = "100px";
        }
        textarea.style.resize = "vertical";
        buttons.style.display = "flex";
    })
 }

 function initReplyAutoFocus(replyFormContainer) {
    replyFormContainer.addEventListener('shown.bs.collapse', function () {
        this.querySelector('textarea').focus();
    })
}

function initCommentStarButton(button) {
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
            fetch(BASE_URL + COMMENT_STAR_PATH, options)
            .then(response => response.json())
            .then(data => {
                console.log(data)
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

function closeCommentForm(cancelButton) {
    var form = cancelButton.closest('.comment-form');
    var textarea = form.querySelector('.comment-form-textarea');
    var buttons = form.querySelector('.comment-form-buttons');
    buttons.style.display = "none";
    textarea.style.height = "1rem";
    textarea.style.resize = "none";
}

function initPreviewMarkdownButton(button) {
    button.addEventListener('click', (e) => {
        e.preventDefault();

        // Get form elements
        var form = button.closest('.comment-form');
        var csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        var textarea = form.querySelector('.comment-form-textarea')
        var markdownPreviewButton = form.querySelector('.comment-form-markdown-preview-button');
        var markdownEditButton = form.querySelector('.comment-form-markdown-edit-button');
        var markdownPreviewContainer = form.querySelector('.comment-form-markdown-preview-container');
        
        // Get safe markdown 
        var formData = new FormData();
        formData.append('content', textarea.value);
        var options = {
            method: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            body: formData
        }
         fetch(BASE_URL + MARKDOWNIFY_PATH, options)
        .then(response => response.json())
        .then(response => {
            if (response.status === '200') {
                // Update and display markdown preview container
                markdownPreviewContainer.innerHTML = response.markdown;
                markdownPreviewContainer.style.display = 'block';
                textarea.style.display = 'none';
            }
        })

    });
}

function initEditMarkdownButton(button) {
    console.log('initing button');
    button.addEventListener('click', (e) => {
        e.preventDefault();
        var form = button.closest('.comment-form');
        var textarea = form.querySelector('.comment-form-textarea');
        var markdownPreviewContainer = form.querySelector('.comment-form-markdown-preview-container');

        // Hide preview container, show edit container 
        markdownPreviewContainer.innerHTML = '';
        markdownPreviewContainer.style.display = 'none';
        textarea.style.display = 'block';

        // Focus at end of textarea content
        const end = textarea.value.length;
        textarea.focus();
        textarea.setSelectionRange(end, end);
    })
}

 function initComments() {
    var commentStarButtons = document.querySelectorAll('.comment-star-button');
    commentStarButtons.forEach(button => {
        initCommentStarButton(button);
    });
    var commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        initCommentForm(form);
        initFormFocus(form);
    });
    var replyFormContainers = document.querySelectorAll('.reply-form-container');
    replyFormContainers.forEach(replyFormContainer => {
        initReplyAutoFocus(replyFormContainer);
    })
    var previewMarkdownButtons = document.querySelectorAll('.comment-form-preview-markdown-button');
    previewMarkdownButtons.forEach(button => {
        initPreviewMarkdownButton(button);
    })
    var editMarkdownButtons = document.querySelectorAll('.comment-form-edit-markdown-button');
    editMarkdownButtons.forEach(button => {
        initEditMarkdownButton(button);
    })
 }

initComments();