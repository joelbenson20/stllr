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

    roomSocket.onopen = function() {
        const heartbeat = setInterval(() => {
            if (roomSocket.readyState === WebSocket.OPEN) {
                roomSocket.send(JSON.stringify({ type: 'ping' }));
            } else {
                clearInterval(heartbeat)
            }
        }, 10000)

        roomSocket.addEventListener('close', () => clearInterval(heartbeat))
    }

    roomSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === "room_message") {
            const isAtBottom = messageFeed.scrollHeight - messageFeed.scrollTop <= messageFeed.clientHeight + 10;
            messageFeed.innerHTML += data.html
            if (isAtBottom) messageFeed.scrollTop = messageFeed.scrollHeight;
        }
        else if (data.type === "presence_update") {
            const roomInfoButton = document.querySelector('#roomInfoButton');
            const roomUserCount = document.querySelector('#roomUserCount');
            const popover = bootstrap.Popover.getInstance(roomInfoButton);
            
            const listHtml = data.users.map(u => `<li class="list-group-item">${u}</li>`).join('');
            const contentHtml = `<ul class="list-group list-group-flush">${listHtml}</ul>`;
            
            roomUserCount.innerText = data.count
            popover.setContent({
                '.popover-header': 'Users present',
                '.popover-body': contentHtml,
            });
        }
    };

    messageTextarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const content = messageTextarea.value;
            if (content) {
                roomSocket.send(JSON.stringify({ content: content }));
                messageTextarea.value = '';
                messageTextarea.style.height = 'auto';
                messageTextarea.focus();
            }
        }
    })

    roomSocket.onclose = function(event) {
        console.error('Room socket closed unexpectedly');
    };

    messageTextarea.addEventListener('input', () => {
        messageTextarea.style.height = 'auto';
        messageTextarea.style.height = messageTextarea.scrollHeight + 'px';
    })

    messageTextarea.focus();
}

initRoom();