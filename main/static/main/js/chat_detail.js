const chat_slug = JSON.parse(document.getElementById("chat_slug").textContent);

const chatDetailSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + chat_slug + '/');

chatDetailSocket.onopen = function(e) {
    console.log("Ok");
};

chatDetailSocket.onclose = function(e) {
    console.error("Websocket disconnect!")
};

chatDetailSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chats_info = data.chats_info;

    const ul_html = document.querySelector("#ul");
    for (let item in chats_info) {
        ul_html.innerHTML += `<li>
                                  <a href="">
                                      ${chats_info[item].name} ${chats_info[item].count_messages}
                                  </a>
                              </li>`;
    };
};