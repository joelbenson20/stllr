const feeder = document.getElementById('pageFeeder');

if (feeder) {
    const parser = new DOMParser();
    let page = 1;
    let loading = false;
    let intersecting = false;

    const loadMore = () => {
        if (loading) return;
        loading = true;
        const params = new URLSearchParams(window.location.search);
        params.set('p', page);
        fetch(feeder.dataset.url + '?' + params.toString())
            .then(r => r.text())
            .then(html => {
                if (html === '') {
                    feeder.remove();
                } else {
                    const doc = parser.parseFromString(html, 'text/html');
                    doc.querySelectorAll('.page').forEach(newPage => {
                        if (!document.getElementById(newPage.id)) {
                            feeder.insertAdjacentElement('beforebegin', newPage);
                        }
                    });
                    page += 1;
                    loading = false;
                    if (intersecting) loadMore();
                }
            });
    };

    new IntersectionObserver(
        entries => {
            intersecting = entries[0].isIntersecting;
            if (intersecting) loadMore();
        },
        { rootMargin: '300px' }
    ).observe(feeder);
}
