const chat_slug = JSON.parse(document.getElementById("chat_slug").textContent);

const chatDetailSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_slug + '/');

chatDetailSocket.onopen = function(e) {
    console.log("Ok");
    chatDetailSocket.send(JSON.stringify({"type": "connect"}));
};

chatDetailSocket.onclose = function(e) {
    console.error("Websocket disconnect!");
};

chatDetailSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message_info = data.message_info;

    if (message_info != "connect") {
        const no_messages = document.querySelector(".no_messages");
        if (no_messages) {
            no_messages.remove();
        };
        const messages_html = document.querySelector(".messages");
        const old_messages = messages_html.innerHTML;
        messages_html.innerHTML = `<div id=message class=unreaded><input type=hidden value=${data.user_id}>
                                        <div class=reply-body>
                                            <strong>
                                                <a class=username href=/user/${message_info.owner_url}>
                                                    ${ message_info.owner_name}
                                                </a>
                                            </strong>
                                            <span class=pub_date>Только что</span>
                                            <p class=text>${message_info.message}</p>
                                        </div>
                                    </div>`;
        messages_html.innerHTML += old_messages;
    };
    let messages = document.querySelectorAll(".unreaded")
    for (let message of messages) {
        if (message.firstChild.value != data.user_id) {
            message.style.backgroundColor = "#FFFFF0";
        };
    };
    document.querySelector("#chat-message-input").focus();
};

document.querySelector("#chat-message-submit").onclick = function(e) {
    const html_message = document.querySelector("#chat-message-input");
    chatDetailSocket.send(JSON.stringify({
            "type": "send_message",
            "message": html_message.value,
        }));
    html_message.value = "";
};