const chat_slug = JSON.parse(document.getElementById("chat_slug").textContent);

const chatDetailSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_slug + '/');

chatDetailSocket.onopen = function(e) {
    console.log("Ok");
};

chatDetailSocket.onclose = function(e) {
    console.error("Websocket disconnect!");
};

chatDetailSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message_info = data.message_info;

    if (data.type == "chat_message") {
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
    }else if (data.type == "update_chat") {
        document.querySelector("#title_chat").innerHTML = `Добро пожаловать в чат "${data.chat_name}"`;
        const close_modal_window = document.querySelector(".close");
        document.location.replace(close_modal_window.href);
        console.log(`${data.chat_name} chat update`);
    }else if (data.type == "message_read") {
        let messages = document.querySelectorAll(".unreaded")
        for (let message of messages) {
            if (message.firstChild.value != data.user_id) {
                message.style.backgroundColor = "#FFFFF0";
            };
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

document.querySelector("#create_button").onclick = function(event) {
    const chat_title = document.querySelector("#input_name");
    const chat_password = document.querySelector("#input_password");
    chat_title.reportValidity();
    if (chat_title.value){
        chatDetailSocket.send(JSON.stringify({
            "chat_title": chat_title.value,
            "chat_password": chat_password.value,
            "chat_id": chat_slug,
            "type": "update_chat",
        }));
    };
};

function delete_chat(e) {
    if (confirm("Вы действительно хотите удалить чат?")) {
        window.location.pathname = `/chat/${chat_slug}/delete/`;
    };
};

function leave_chat(e) {
    if (confirm("Вы действительно хотите выйти из чата?")) {
        window.location.pathname = `/chat/${chat_slug}/leave/`;
    };
};