import json
import socket
import threading

from classes.shared import User, UserMessage

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(('127.0.0.1', 65431))
serv.listen(5)

users = []
message_train = []

def handle_user(conn, addr):
    user = None
    buffer = ""

    try:
        while True:
            print(f"{addr} : Waiting for data...")
            data = conn.recv(4096)
            print(f"{addr} : Received data : {data}")

            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if not line:
                    continue

                json_output = json.loads(line)

                if user is None:
                    user = User(
                        user_id=json_output["user_id"],
                        user_room=4512,
                        conn=conn
                    )

                    users.append(user)
                    continue

                if json_output["user_action"] == "bye":
                    return

                message = UserMessage(
                    user_id=json_output["user_id"],
                    user_message=json_output["user_message"]
                )
                message_train.append(message)

                json_messages = [
                    {
                        "user_id": message.user_id,
                        "user_message": message.user_message
                    }
                    for message in message_train
                ]

                data = (json.dumps(json_messages) + "\n").encode()
        
                for user_client in users:
                    print(f"Sending: {message.user_message} : {user_client}")
                    user.conn.sendall(data)
                    print(f"Sent: {message.user_message} : {user_client}")
            
    except (ConnectionResetError, BrokenPipeError): print(f"{addr} disconnected unexpectedly") 

    except Exception as e: print(f"Error with {addr}: {e}")  # noqa: BLE001

    finally:
        if user is not None and user in users:
            users.remove(user)

        conn.close()
        


while True:
    conn, addr = serv.accept()

    thread = threading.Thread(target=handle_user, args=(conn, addr))

    thread.start()
