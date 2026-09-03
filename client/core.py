# Main imports
import json
import socket

from classes.shared import UserMessage

class ChatClient:

    def __init__(self, user_id):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', 65431))
        
        self.user_id = user_id
        
        self.message_train = []

    def debug(self, message):
        with open("debug.txt", "a") as f:
            f.write(str(message) + "\n")
    
    def receive_messages(self):

        buffer = ""

        while True:
            try:
                self.debug("Waiting for data...")
                data = self.client.recv(4096)
                self.debug(f"Recv: {data}")

                if not data: break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if not line:
                        continue

                    json_output = json.loads(line)

                    self.debug(f"PARSED: {json_output}")

                    self.message_train.clear()

                    for message in json_output:
                        self.message_train.append(UserMessage(user_id=message['user_id'], user_message=message['user_message']))
            except ConnectionResetError:
                print("Server disconnected.")
                break

    def send(self, action, message):
        message = {
                "user_id": self.user_id,
                "user_action": action,
                "user_message": message
            }
        
        self.client.sendall((json.dumps(message) + "\n").encode())

    def Run(self):

        self.debug("Running!")

        self.send(action="message", message=f"{self.user_id} has joined")

        self.receive_messages()

            # user_input = input("> ")

            # if user_input == "/bye":
            #     self.send("bye", "")
            #     break

            # self.send("message", user_input)

            # print(self.message_train)
        