const parser = new DOMParser();
var page = 1;
var emptyPage = false;
var blockRequest = false;

const loadMorePages = () => {
    var margin = document.body.clientHeight - window.innerHeight - 300;
    if (window.pageYOffset > margin && !emptyPage && !blockRequest) {
        blockRequest = true;
        page += 1;
        const params = new URLSearchParams(window.location.search);
        params.set('cards_only', '1');
        params.set('p', page);
        fetch('?' + params.toString())
        .then(response => response.text())
        .then(html => {
            if (html === '') {
                emptyPage = true;
            }
            else {
                var pageFeed = document.getElementById('pageFeed');
                var newHTML = parser.parseFromString(html, 'text/html');
                var newPages = newHTML.querySelectorAll('.page');

                newPages.forEach(newPage => {
                    newPageId = newPage.id
                    if (!document.querySelector(`#${newPageId}`)){
                        pageFeed.insertAdjacentElement('beforeend', newPage);
                    }
                })
                blockRequest = false;
            }
        })
    }
};

window.addEventListener('scroll', _.throttle(loadMorePages, 500, { leading: true }));
