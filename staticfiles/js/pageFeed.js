var page = 1;
var emptyPage = false;
var blockRequest = false;

window.addEventListener('scroll', function(e) {
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
                var pageFeed = document.getElementById('page-feed');
                pageFeed.insertAdjacentHTML('beforeend', html);
                blockRequest = false;
            }
        })
    }
})

const scrollEvent = new Event('scroll');
window.dispatchEvent(scrollEvent);
