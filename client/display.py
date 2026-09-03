import threading
import asyncio

from textual import work
from classes.shared import UserMessage
from textual.app import App
from client.core import ChatClient
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Collapsible, Digits, Footer, Label, Markdown, Header, Input, Log, Button

INSTRUCT_MD = """\
This is a super simple server authoritative terminal chat app

# The Server
To start up a server on the local network simply run the main.py file and when it prompts you select Server.
This will open up a separate terminal window with controls to kick, ban, and mute people.

To shut down the server simple click finish, give it a second and then it will close down.

# The Client
To start up a client on the local network simply run the main.py file and when it prompts you select Client.
This will connect you to the local network for the terminal chat and to anyone else running the server file.

With this you are able to:
- Set your username
- Join and leave rooms
- Create private rooms
- Play RPG games w/ friends

# Client & Server
You are able to from the main boot-up dashboard start both the client and the server and use the server as a user instead of as the server.

To close all of these simply close the window and it will shut down
To update press check for updates or update in the main dashboard
"""

class ClientChat(App):
    CSS = """
        Horizontal {
            height: auto;
        }

        Horizontal Input {
            width: 1fr;
        }
        """

    def __init__(self, driver_class = None, css_path = None, watch_css = False, ansi_color = None):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.client = ChatClient(user_id="")
        self.message_log = Log(auto_scroll=True, name="Chat")
        self.last_message_count = 0

        self.user_id_input = Input(placeholder="User_ID", type="text")
        self.user_message_input = Input(placeholder="", type="text")
        self.user_id_join = Button(label="Join", id="join")
        self.user_id_send = Button(label="Send", id="send")

        self.user_message_input.visible = False
        self.user_id_send.visible = False

    def debug(self, message):
        with open("debug_client_display.txt", "a") as f:
            f.write(str(message) + "\n")

    def compose(self) -> ComposeResult:
        yield Header()
        with Collapsible(
                title="Info",
                collapsed_symbol="?",
                expanded_symbol="▼",
                collapsed=True
            ):
                yield Markdown(INSTRUCT_MD)

        with Horizontal():
             yield self.user_id_input
             yield self.user_id_join

        yield self.message_log

        with Horizontal():
            yield self.user_message_input
            yield self.user_id_send

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "join":
            self.client = ChatClient(user_id=self.user_id_input.value)
            self.client_thread = threading.Thread(target=self.client.Run,daemon=True)
            self.client_thread.start()
            self.watch_messages()
            self.user_id_input.visible = False
            self.user_id_join.visible = False
            self.user_message_input.visible = True
            self.user_id_send.visible = True
        elif event.button.id == "send":
            self.client.send(self.client.user_id, self.user_message_input.value)
            self.user_message_input.value = ""
    @work
    async def watch_messages(self):
        while self.client is not None:
            messages = self.client.message_train.copy()
            if len(messages) > self.last_message_count:
                new_messages = messages[self.last_message_count:]
                for message in new_messages:
                    self.message_log.write_line(f"{message.user_id}> {message.user_message}")
                self.last_message_count = len(messages)
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    app = ClientChat()
    app.run()
