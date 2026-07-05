document.addEventListener('click', (e) => {
    const btn = e.target.closest('.crew-invitation-btn');
    if (!btn) return;
    const wrapper = btn.closest('.crew-invitation-btns');
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
        const tmp = document.createElement('div');
        tmp.innerHTML = html.trim();
        wrapper.replaceWith(tmp.firstElementChild);
    })
    .catch(() => { btn.disabled = false; });
});
