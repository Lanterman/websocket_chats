# Websocket chats

This project represents chats in real life and has the following functionality:
- registration / authorization;
- creating / deleting a chat, as well as joining / leaving it if you are not its owner;
- send messages in real life;
- search chats;
- etc.

Project tested with: TestCase, WebsocketCommunicator, ChannelsLiveServerTestCase.

The project is also analyzed by selenium and asynchronous parses.

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

### Running parsers

#### 1) Selenium parser
```
python parsing/parsing_with_selenium.py
```
#### 2) Asynchronous parser
```
python parsing/asyncio_parser.py
```