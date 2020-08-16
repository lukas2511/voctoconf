const chat_message_template = document.querySelector('#chat_message');

function scrollChatDown() {
    document.querySelector('#chat-scroll-container').scrollTo(0, document.querySelector('#chat-scroll-container').scrollHeight)
}
scrollChatDown();

var chatSocket;
function connect() {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    if (window.location.protocol == 'https:' ) {
        chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/' + roomName + '/');
    } else {
        chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomName + '/');
    }
    chatSocket.onopen = function() {
        console.log('WS connected')
    };

    chatSocket.onmessage = function(e) {
        console.debug('WS message:', e.data);
        const message = JSON.parse(e.data).message;

        const chat = document.querySelector('#chat-log > tbody');
    
        // Clone the new row and insert it into the table
        const clone = chat_message_template.content.cloneNode(true);
        var td = clone.querySelectorAll("td");
        td[0].textContent = message.date;
        td[1].textContent = message.sender;
        td[2].textContent = message.content;
        chat.appendChild(clone);

        // remove old messages
        if(chat.childNodes.length>150)
        chat.removeChild(chat.childNodes[0]);
        scrollChatDown();
    };

    chatSocket.onclose = function(e) {
        console.log('WS is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function() {
        connect();
        }, 1000);
    };

    chatSocket.onerror = function(err) {
        console.error('WS encountered error: ', err.message, 'Closing socket');
        ws.close();
    };
}

connect();

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};
    
document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'type': 'chat_message',
        'message': message
    }));
    messageInputDom.value = '';
    scrollChatDown();
};

scrollChatDown();