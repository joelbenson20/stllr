document.addEventListener('click', (e) => {
    const btn = e.target.closest('.contact-action-btn');
    if (!btn) return;

    const wrapper = btn.closest('[id^="contact-btn-"]');
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
