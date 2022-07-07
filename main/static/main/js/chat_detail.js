const chat_slug = JSON.parse(document.getElementById("chat_slug").textContent);

const chatDetailSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_slug + '/');

chatDetailSocket.onopen = function(e) {
    console.log("Ok");
    is_read();
    if (is_new_user.value == 1) {
        chatDetailSocket.send(JSON.stringify({
            "type": "connect_to_chat",
        }));
        fetch(`${window.location.pathname}connect/`)
            .then(response => console.log('Successfully'))
            .catch(error => console.log('Error'))
    };
};

chatDetailSocket.onclose = function(e) {
    console.error("Websocket disconnect!");
};

chatDetailSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type == "chat_message") {
        const message_info = data.message_info;
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
        is_read();
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
    }else if (data.type =="connect_to_chat") {
        const user_info = data.user_info;
        const user_list = document.querySelector("#list_users");
        const new_user = `<p><a class=redirect href=/user/${user_info.owner_url}>${user_info.owner_name}</a></p>`
        user_list.innerHTML += new_user;
    }else if (data.type == "disconnect_to_chat") {
        document.querySelector(`#user_${data.user_username}`).remove()
    };
    document.querySelector("#chat-message-input").focus();
};

function is_read() {
    fetch(`${window.location.pathname}is_read/`);
}

function send_message(e) {
    const html_message = document.querySelector("#chat-message-input");
    html_message.reportValidity();
    if (html_message.value) {
        chatDetailSocket.send(JSON.stringify({
                "type": "send_message",
                "message": html_message.value,
            }));

        let data = new FormData();
        data.append("message", `${html_message.value}`)
        fetch(`${window.location.pathname}add_message/`, {method: 'POST', body: data});

        html_message.value = "";
    };
};

function submit_data(event) {
    const chat_title = document.querySelector("#input_name");
    const chat_password = document.querySelector("#input_password");
    chat_title.reportValidity();
    if (chat_title.value){
        chatDetailSocket.send(JSON.stringify({
            "chat_title": chat_title.value,
            "type": "update_chat",
        }));
        let data = new FormData();
        data.append("title", `${chat_title.value}`)
        data.append("password", `${chat_password.value}`)
        fetch(`${window.location.pathname}update_chat/`, {method: 'POST', body: data});
    };
};

function delete_chat(e) {
    if (confirm("Вы действительно хотите удалить чат?")) {
        window.location.pathname = `/chat/${chat_slug}/delete/`;
    };
};

function leave_chat(e) {
    if (confirm("Вы действительно хотите выйти из чата?")) {
        chatDetailSocket.send(JSON.stringify({
            "type": "disconnect_to_chat",
        }));
        window.location.pathname = `chat/${chat_slug}/leave/`;
    };
};