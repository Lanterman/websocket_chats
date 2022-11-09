# Websocket chats

This project represents chats in real life and has the following functionality:
- registration / authorization;
- creating / deleting a chat, as well as joining / leaving it if you are not its owner;
- send messages in real life;
- search chats;
- etc.

Project tested with: TestCase, WebsocketCommunicator, ChannelsLiveServerTestCase.

The project is also parsed with selenium.

### Launch of the project

#### 1) clone the repository
```
git clone https://github.com/Lanterman/websocket_chats.git
```
#### 2) Create and run docker-compose
```
docker-compose up --build
```
#### 3) Follow the link in the browser
```
http://127.0.0.1:8000/
```
or
```
http://0.0.0.0:8000/
```

### Launch of the tests

#### 1) Run command
```
python manage.py test
```

### Launch of the selenium parser

#### 1) Run command
```
python parsing/parsing_with_selenium.py
```