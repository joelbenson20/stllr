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

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.crew-action-btn');
    if (!btn) return;
    const wrapper = btn.closest('[id^="crew-btn-"]');
    btn.disabled = true;

    fetch(new URL(btn.dataset.endpoint, document.baseURI).href, {   // TODO: Separate forums/posts.js and forums/forms.js.
        method: 'POST',
        headers: {
            'X-CSRFToken': btn.dataset.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        mode: 'same-origin',
    })
    .then(r => {
        if (!r.ok) { window.location.href = btn.dataset.endpoint; return null; }
        return r.text();
    })
    .then(html => {
        if (!html) return;
        const tmp = document.createElement('div');
        tmp.innerHTML = html.trim();
        wrapper.replaceWith(tmp.firstElementChild);
    })
    .catch(() => { btn.disabled = false; });
});

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.crew-invite-btn');
    if (!btn) return;

    btn.disabled = true;
    fetch(new URL(btn.dataset.endpoint, document.baseURI).href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': btn.dataset.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        mode: 'same-origin',
    })
    .then(r => {
        if (r.ok) {
            btn.textContent = 'Invited';
        } else {
            btn.disabled = false;
        }
    })
    .catch(() => { btn.disabled = false; });
});

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.crew-member-action-btn');
    if (!btn) return;

    const row = btn.closest('.crew-member-row');
    btn.disabled = true;

    fetch(new URL(btn.dataset.endpoint, document.baseURI).href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': btn.dataset.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        mode: 'same-origin',
    })
    .then(r => {
        if (!r.ok) { btn.disabled = false; return null; }
        return r.text();
    })
    .then(html => {
        if (html === null) return;
        if (html.trim() === '') {
            row.remove();
        } else {
            const tmp = document.createElement('div');
            tmp.innerHTML = html.trim();
            row.replaceWith(tmp.firstElementChild);
        }
    })
    .catch(() => { btn.disabled = false; });
});
