const initBeaconFeed = (feeder) => {
    let loading = false;
    let intersecting = false;

    const loadMore = (attempt = 0) => {
        if (loading) return;
        loading = true;
        const params = new URLSearchParams();
        if (feeder.dataset.beaconedToCrewId) params.set('beaconed_to_crew_id', feeder.dataset.beaconedToCrewId);
        if (feeder.dataset.beaconedToUserId) params.set('beaconed_to_user_id', feeder.dataset.beaconedToUserId);
        params.set('p', feeder.dataset.p);
        fetch(new URL(feeder.dataset.endpoint, document.baseURI).href + '?' + params.toString())
            .then(r => r.text())
            .then(html => {
                if (html === '') {
                    feeder.remove();
                } else {
                    const tmp = document.createElement('div');
                    tmp.innerHTML = html;
                    const items = [...tmp.querySelectorAll('.beacon')];
                    items.forEach((item, i) => {
                        setTimeout(() => {
                            feeder.insertAdjacentElement('beforebegin', item);
                            item.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
                        }, i * 80);
                    });
                    setTimeout(() => {
                        feeder.dataset.p = parseInt(feeder.dataset.p) + 1;
                        loading = false;
                        if (intersecting) loadMore();
                    }, items.length * 80);
                }
            })
            .catch(() => {
                loading = false;
                if (attempt < 3) {
                    const delay = 1000 * 2 ** attempt + Math.random() * 1000;
                    setTimeout(() => loadMore(attempt + 1), delay);
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
};

document.querySelectorAll('.beacon-feeder').forEach(initBeaconFeed);

new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
            if (node.nodeType !== Node.ELEMENT_NODE) continue;
            if (node.matches('.beacon-feeder')) initBeaconFeed(node);
            node.querySelectorAll('.beacon-feeder').forEach(initBeaconFeed);
        }
    }
}).observe(document.body, { childList: true, subtree: true });
