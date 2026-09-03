class UserMessage:
    def __init__(self, user_id, user_message):
        self.user_id = user_id
        self.user_message = user_message

class User:
    def __init__(self, user_id, user_room, conn):
        self.user_id = user_id
        self.user_room = user_room
        self.conn = conn