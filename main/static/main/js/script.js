const chatsSocket = new WebSocket('ws://' + window.location.host + '/ws/chats/');

chatsSocket.onopen = function(e) {
    console.log("Ok");
};

chatsSocket.onclose = function(e) {
    console.error("Websocket disconnect!")
};

chatsSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const log_messages = document.querySelector("#log");
    log_messages.innerHTML += data.message + "\n";
};

document.querySelector("#button").onclick = function(e) {
    const input_text = document.querySelector("#input_text");
    chatsSocket.send(JSON.stringify({"message": input_text.value}));
    input_text.value = "";
};