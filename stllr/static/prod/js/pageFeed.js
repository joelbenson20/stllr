const parser = new DOMParser();
var page = 1;
var emptyPage = false;
var blockRequest = false;

const loadMorePages = () => {
    var margin = document.body.clientHeight - window.innerHeight - 200;
    if (window.pageYOffset > margin && !emptyPage && !blockRequest) {
        blockRequest = true;
        page += 1;
        fetch('?cards_only=1&p=' + page)
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
                        pageFeed.insertAdjacentElement('beforeend', page);
                    }
                })
                blockRequest = false;
            }
        })
    }
};

window.addEventListener('scroll', _.throttle(loadMorePages, 500, { leading: true }));
