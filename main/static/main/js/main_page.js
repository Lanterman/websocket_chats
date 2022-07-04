const mainSocket = new WebSocket('ws://' + window.location.host + '/ws/main/');

mainSocket.onopen = function(e) {
    console.log("Ok");
};

mainSocket.onclose = function(e) {
    console.error("Websocket disconnect!");
};

mainSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type == "search") {
        const chats_info_list = data.chats_info_list;
        const chats_without_me = document.querySelector("#chats_without_me");
        chats_without_me.innerHTML = "";
        for (let chat of chats_info_list) {
            let chatHTML = `<div class="chat_without_me">
                                <p class="chat_name"><a class="redirect" href=${chat.chat_url}>${chat.chat_name}</a></p>
                                <p class="chat_owner_name">
                                    <a class="redirect" href="${chat.chat_owner_url}">${chat.chat_owner_name}</a>
                                </p>
                                <p class="is_password">Частный: <i>${chat.is_password}</i></p>
                            </div>`;
            chats_without_me.innerHTML += chatHTML;
        };
        if (!chats_info_list.length) {
            chats_without_me.innerHTML = '<p id="no_groups"><i>Нет групп соответствующих запросу!</i></p>'
        };
    }else{
        document.querySelector(`#chat_${data.chat_id}`).remove();
        console.log(`${data.chat_id} chat deleted`);
    };
};

document.querySelector(".search_button").onclick = function(e) {
    const search_input = document.querySelector(".input");
    search_input.reportValidity()
    if (search_input.value) {
        mainSocket.send(JSON.stringify({
            "search_value": search_input.value,
            "type": "search",
        }));
    };
    search_input.value = "";
};

function content_menu(event, chat_name, chat_id) {
    event.preventDefault();
    if (confirm(`Вы действительно хотите удалить ${chat_name}?`)) {
        mainSocket.send(JSON.stringify({
            "chat_id": chat_id,
            "type": "delete_chat",
        }));
    };
};