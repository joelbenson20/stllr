document.addEventListener('click', (e) => {
    const btn = e.target.closest('.crew-action-btn');
    if (!btn) return;

    const wrapper = btn.closest('[id^="crew-btn-"]');
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
