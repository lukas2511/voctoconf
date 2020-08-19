const chat_message_template = document.querySelector('#chat_message');
const whisper_message_received_template = document.querySelector('#whisper_message_received');
const whisper_message_sent_template = document.querySelector('#whisper_message_sent');
const system_message_template = document.querySelector('#system_message');

class Chat{
    connected = false;
    socket = null;
    roomName = null;
    
    container = null;
    scrollContainer = null;
    log = null;
    input = null;
    submitButton = null;

    constructor(container, roomName){
        this.container = container;
        this.roomName = roomName;

        this.input = this.container.querySelector('[data-chat-input]');
        this.scrollContainer = this.container.querySelector('[data-chat-scroll-container]');
        this.log = this.scrollContainer.querySelector('[data-chat-log]');
        this.submitButton = this.container.querySelector('[data-chat-submit]');

        this.scrollDown();
        this.input.focus();
        this.container.addEventListener('click',this.onActionClicked.bind(this));

        this.submitButton.addEventListener('click', this.submit.bind(this));
        this.input.addEventListener('keyup', (e) => {
            if (e.keyCode === 13)
                this.submitButton.click();
        });
    }

    connect(){
        if (window.location.protocol == 'https:' ) {
            this.socket = new WebSocket('wss://' + window.location.host + '/ws/chat/' + this.roomName + '/');
        } else {
            this.socket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + this.roomName + '/');
        }
        this.socket.onmessage = this.onMessage.bind(this);
        this.socket.onopen = this.onOpen.bind(this);
        this.socket.onclose = this.onClose.bind(this);
        this.socket.onerror = this.onError.bind(this);
    }


    onMessage(e) {
        console.debug('Chat message received:', e.data);
        const data = JSON.parse(e.data);
        const type = data.type;
        const message = data.message;
        let name = message.sender;
        
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
        if (message.sender)
            clone.querySelectorAll('[data-chat-sender]').forEach((e)=>e.textContent = message.sender);
        if (message.receiver)
            clone.querySelectorAll('[data-chat-receiver]').forEach((e)=>e.textContent = message.receiver);
        clone.querySelectorAll('[data-chat-name]').forEach((e)=>e.setAttribute('data-chat-name', name));
        clone.querySelector('[data-chat-date]').textContent = message.date;
        clone.querySelector('[data-chat-content]').textContent = message.content;
        this.log.appendChild(clone);

        // remove old messages
        if(this.log.childNodes.length>150)
            this.log.removeChild(this.log.childNodes[0]);
        
        this.scrollDown();
    }

    submit(){
        if(!this.connected)
            return;
        const content = this.input.value;
        if( content.startsWith("/w ") ||
            content.startsWith("/msg ") ||
            content.startsWith("/whisper ") ){
            const components = content.split(" ");
            if(components[1]){
                this.socket.send(JSON.stringify({
                    'type': 'whisper_message',
                    'content': components.slice(2).join(" "),
                    'receiver': components[1]
                }));
            }
        } else if( content.startsWith("/ban ") ){
            const components = content.split(" ");
            if(components[1]){
                this.socket.send(JSON.stringify({
                    'type': 'ban',
                    'content': components.slice(2).join(" "),
                    'receiver': components[1]
                }));
            }
        } else if( content.startsWith("/pardon ") ){
            const components = content.split(" ");
            if(components[1]){
                this.socket.send(JSON.stringify({
                    'type': 'pardon',
                    'receiver': components[1]
                }));
            }
        } else if( content.startsWith("/users") ){
            if(components[1]){
                this.socket.send(JSON.stringify({
                    'type': 'userlist'
                }));
            }
        } else if( content.startsWith("/system ") ){
            const components = content.split(" ");
            this.socket.send(JSON.stringify({
                'type': 'system_message',
                'content': components.slice(1).join(" ")
            }));
        } else if( content == "/userlist" ){
            this.socket.send(JSON.stringify({
                'type': 'userlist'
            }));
        } else {
            if (content.trim()){
                this.socket.send(JSON.stringify({
                    'type': 'chat_message',
                    'content': content
                }));
            }
        }

        this.input.value = '';
        this.scrollDown();
    }

    onActionClicked(event){
        const target = event.target.closest('[data-chat-action=whisper][data-chat-name],[data-chat-action=ban][data-chat-name]');
        if (!target)
            return;
        
        event.preventDefault();
        
        const action = target.getAttribute('data-chat-action');
        if (action == 'whisper' || action == 'ban'){
            const message = this.input.value;
            let prefix;
            if (action == 'whisper'){
                prefix = `/w ${target.getAttribute('data-chat-name')} `
            } else if (action == 'ban') {
                prefix = `/ban ${target.getAttribute('data-chat-name')} `
            }
    
            if(!message.startsWith(prefix))
                this.input.value = prefix + message;
                this.input.focus();
        }
    }

    onOpen(){
        console.debug('Connected to chat.');
        this.connected = true;
    }
    
    onClose(e){
        console.warn('Chat connection lost. Reconnect will be attempted in 1 second.', e.reason);
        this.connected = false;
        setTimeout(()=>this.connect(), 1000);
    };

    onError(e){
        console.error('Chat encountered error: ', e.message, 'Closing socket');
        this.socket.close();
    }

    scrollDown(){
        this.scrollContainer.scrollTo(0, this.scrollContainer.scrollHeight)
    }
}

new Chat(
    document.querySelector('#chat'),
    JSON.parse(document.getElementById('room-name').textContent)
).connect();

