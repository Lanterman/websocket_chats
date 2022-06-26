import json
from channels.generic.websocket import WebsocketConsumer


class ChatsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        json_text_data = json.loads(text_data)
        message = json_text_data["message"]
        self.send(text_data=json.dumps({'message': message}))
