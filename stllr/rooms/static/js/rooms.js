function initRoom() {
    const pageId = JSON.parse(
        document.getElementById('pageId').textContent
    );
    const requestUser = JSON.parse(
        document.getElementById('requestUser').textContent
    );
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const url = wsProtocol + window.location.host + '/ws/room/' + pageId + '/';
    const roomSocket = new WebSocket(url);
    const messageTextarea = document.querySelector('.message-textarea');
    const messageFeed = document.querySelector('.message-feed');

    messageTextarea.addEventListener('input', () => {
        messageTextarea.style.height = 'auto';
        messageTextarea.style.height = messageTextarea.scrollHeight + 'px';
    })

    roomSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        messageFeed.innerHTML += data.html
        messageFeed.scrollTop = messageFeed.scrollHeight;
    };

    messageTextarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const content = messageTextarea.value;
            if (content) {
                roomSocket.send(JSON.stringify({'content': content}));
                messageTextarea.value = '';
                messageTextarea.style.height = 'auto';
                messageTextarea.focus();
            }
        }
    })

    roomSocket.onclose = function(event) {
        console.error('Room socket closed unexpectedly');
    };

    messageTextarea.focus();
}

initRoom();