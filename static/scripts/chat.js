const chat_message_template = document.querySelector('#chat_message');
const whisper_message_received_template = document.querySelector('#whisper_message_received');
const whisper_message_sent_template = document.querySelector('#whisper_message_sent');
const system_message_template = document.querySelector('#system_message');

function scrollChatDown() {
    document.querySelector('#chat-scroll-container').scrollTo(0, document.querySelector('#chat-scroll-container').scrollHeight)
}

var chatConnected = false;
var chatSocket;
function connect() {
    const roomName = JSON.parse(document.getElementById('room-name').textContent);

    if (window.location.protocol == 'https:' ) {
        chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/' + roomName + '/');
    } else {
        chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomName + '/');
    }
    chatSocket.onopen = function() {
        console.debug('Connected to chat.');
        chatConnected = true;
    };

    chatSocket.onmessage = function(e) {
        console.debug('Chat message received:', e.data);
        const data = JSON.parse(e.data);
        const type = data.type;
        const message = data.message;
        let name = message.sender;

        const chat = document.querySelector('#chat-log > tbody');
        let template;
        if(type=='chat_message'){
            template = chat_message_template;
        } else if(type=='whisper_message') {
            if(data.sent){
                template = whisper_message_sent_template
                name = message.receiver
            } else {
                template = whisper_message_received_template
            }
        } else if(type=='system_message') {
            template = system_message_template
        }
    
        // Clone the new row and insert it into the table
        const clone = template.content.cloneNode(true);
        clone.querySelectorAll('[data-chat-name]').forEach((e)=>e.setAttribute('data-chat-name', name));
        clone.querySelector('[data-chat-date]').textContent = message.date;
        if(name)
            clone.querySelector('[data-chat-name]').textContent = name;
        clone.querySelector('[data-chat-content]').textContent = message.content;
        chat.appendChild(clone);

        // remove old messages
        if(chat.childNodes.length>150)
        chat.removeChild(chat.childNodes[0]);
        scrollChatDown();
    };

    chatSocket.onclose = function(e) {
        console.warn('Chat connection lost. Reconnect will be attempted in 1 second.', e.reason);
        chatConnected = false;
        setTimeout(function() {
            connect();
        }, 1000);
    };

    chatSocket.onerror = function(err) {
        console.error('Chat encountered error: ', err.message, 'Closing socket');
        chatSocket.close();
    };
}

connect();

document.body.addEventListener("click",function(event){
    const target = event.target.closest('[data-chat-action=whisper][data-chat-name],[data-chat-action=ban][data-chat-name]');
    if (!target)
        return;
    
    event.preventDefault();
    
    const action = target.getAttribute('data-chat-action');
    if (action == 'whisper' || action == 'ban'){
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        let prefix;
        if (action == 'whisper'){
            prefix = `/w ${target.getAttribute('data-chat-name')} `
        } else if (action == 'ban') {
            prefix = `/ban ${target.getAttribute('data-chat-name')} `
        }

        if(!message.startsWith(prefix))
            messageInputDom.value = prefix + message;
        messageInputDom.focus();
    }
        
})

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};
    
document.querySelector('#chat-message-submit').onclick = function(e) {
    if(!chatConnected)
        return;
    const messageInputDom = document.querySelector('#chat-message-input');
    const content = messageInputDom.value;
    if( content.startsWith("/w ") ||
        content.startsWith("/msg ") ||
        content.startsWith("/whisper ") ){
        const components = content.split(" ");
        if(components[1]){
            chatSocket.send(JSON.stringify({
                'type': 'whisper_message',
                'content': components.slice(2).join(" "),
                'receiver': components[1]
            }));
        }
    } else if( content.startsWith("/ban ") ){
        const components = content.split(" ");
        if(components[1]){
            chatSocket.send(JSON.stringify({
                'type': 'ban',
                'content': components.slice(2).join(" "),
                'receiver': components[1]
            }));
        }
    } else if( content.startsWith("/pardon ") ){
        const components = content.split(" ");
        if(components[1]){
            chatSocket.send(JSON.stringify({
                'type': 'pardon',
                'receiver': components[1]
            }));
        }
    } else if( content.startsWith("/system ") ){
        const components = message.split(" ");
        chatSocket.send(JSON.stringify({
            'type': 'system_message',
            'content': components.slice(1).join(" ")
        }));
    } else {
        if (content.trim()){
            chatSocket.send(JSON.stringify({
                'type': 'chat_message',
                'content': content
            }));
        }
    }
    
    messageInputDom.value = '';
    scrollChatDown();
};

scrollChatDown();