const pageVoteUrl = 'http://127.0.0.1:8000/page/vote/';
const pageVoteButtons = document.querySelectorAll('a.page-vote-button')

function initPageVoteButtons() {
    pageVoteButtons.forEach(voteButton => {
        voteButton.addEventListener('click', function(e) {
            e.preventDefault();
            var formData = new FormData();
            formData.append('id', voteButton.dataset.id)
            formData.append('action', voteButton.dataset.action);
            var options = {
                method: 'POST',
                headers: {'X-CSRFToken': voteButton.dataset.csrfToken},
                mode: 'same-origin',
                body: formData
            }
            fetch(pageVoteUrl, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 'ok') {

                    var previousAction = voteButton.dataset.action;
                    var newAction = previousAction === 'vote' ? 'unvote' : 'vote';
                    voteButton.dataset.action = newAction

                    var voteCount = voteButton.querySelector('.vote-count');
                    var previousCount = parseInt(voteCount.textContent);
                    voteCount.textContent = previousAction === 'vote' ? previousCount + 1 : previousCount - 1;
                }
            })
        })
    })
}

initPageVoteButtons();



// function initFloatButtons() {

//     const float_buttons = document.querySelectorAll('button.float-button[data-page-id]');

//     float_buttons.forEach(button => {
//         button.addEventListener('click', async (event) => {
//             event.preventDefault();

//             const page_id = button.dataset.pageId;
//             const csrfToken = button.dataset.csrfToken;
//             if (!page_id || !csrfToken) {
//                 return;
//             }

//             fetch(`${FLOAT_API_URL}/page_float/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': csrfToken
//                 },
//                 credentials: 'include',
//                 body: JSON.stringify({ page_id: page_id })
//             })
//             .then(response => response.json())
//             .then(response => {
//                 console.log('Response:', response);
//                 updateFloatButton(button, response.status, response.num_votes);
//             })
//             .catch(error => console.error('Error:', error));
//         });
//     });

// };

// function updateFloatButton(button, status, num_votes) {
//     // If a vote was successfully created
//     if (status === '201') {
//         button.dataset.floated = 'true';
//     }
//     // If a vote was successfully deleted
//     else if (status === '410') {
//         button.dataset.floated = 'false';
//     }

//     //Update float count
//     let floatCount = button.closest('.floats-badge').querySelector('.float-count');
//     floatCount.textContent = num_votes;
// }

// initFloatButtons();