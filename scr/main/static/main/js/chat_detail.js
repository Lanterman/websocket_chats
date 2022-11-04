const chat_slug = JSON.parse(document.getElementById("chat_slug").textContent);

const chatDetailSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_slug + '/');

chatDetailSocket.onopen = function(e) {
    console.log("Ok");
    connect_to_chat();
};

chatDetailSocket.onclose = function(e) {
    console.error("Websocket disconnect!");
};

chatDetailSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messages_html = document.querySelector(".messages");
    if (data.type == "chat_message" | data.type =="connect_to_chat") {
        const no_messages = document.querySelector(".no_messages");
        if (no_messages) {
            no_messages.remove();
        };
    };
    if (data.type == "chat_message") {
        const message_info = data.message_info;
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
        const new_user = `<p id=user_${user_info.owner_url}>
                              <a class=redirect href=/user/${user_info.owner_url}>${user_info.owner_name}</a>
                          </p>`
        user_list.innerHTML += new_user;

        const old_messages = messages_html.innerHTML;
        messages_html.innerHTML = `<p id=user_action>${user_info.owner_url} присоединился к чату!</p>`;
        messages_html.innerHTML += old_messages;

    }else if (data.type == "disconnect_from_chat") {
        document.querySelector(`#user_${data.user_username}`).remove()

        const old_messages = messages_html.innerHTML;
        messages_html.innerHTML = `<p id=user_action>${data.user_username} вышел из чата!</p>`;
        messages_html.innerHTML +=old_messages;
    };
    document.querySelector("#chat-message-input").focus();
};

function connect_to_chat() {
    if (is_new_user.value == 1) {
        chatDetailSocket.send(JSON.stringify({
            "type": "connect_to_chat",
        }));
        let data = new FormData();
        data.append("agree", "True")
        fetch(`${window.location.pathname}connect/`, {method: "POST", body: data})
    };
};

function send_message(e) {
    const html_message = document.querySelector("#chat-message-input");
    html_message.reportValidity();
    if (html_message.value) {
        chatDetailSocket.send(JSON.stringify({
                "type": "send_message",
                "message": html_message.value,
            }));

        const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const request = new Request(window.location.pathname, {headers: {'X-CSRFToken': csrf_token}});
        let data = new FormData();
        data.append("message", html_message.value)
        fetch(request, {method: 'POST', body: data})

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

        const close_modal_window = document.querySelector(".close");
        document.location.replace(close_modal_window.href);
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
            "type": "disconnect_from_chat",
        }));
        window.location.pathname = `chat/${chat_slug}/leave/`;
    };
};