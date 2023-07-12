import json
import queue
import socket
import threading
import time
import uuid

server = socket.gethostbyname(socket.gethostname())
# server = "192.168.1.114"
# server = "192.168.1.113"
# server = "192.168.56.1"

BYTES = 4 * 1024


def read_messages(q):
    while True:
        q.put(input())


def run_client(send_queue, receive_queue, client_uuid):
    host = server
    port = 5050       # Server port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    message = f'{{"uuid": "{client_uuid}"}}'

    try:
        client_socket.connect((host, port))
        while True:
            client_socket.sendall(message.encode())

            # Receive the server's response
            response = client_socket.recv(BYTES).decode()
            # print('Server response:', response)
            if not response:
                continue
            try:
                r_dict = json.loads(response)
            except json.decoder.JSONDecodeError as e:
                print("[E] decode error", e)
                r_dict = {}
            new_mess = r_dict.get('new_mess')

            # if new_mess:
            #     receive_queue.put(new_mess)
            receive_queue.put(r_dict)

            if send_queue.qsize() > 0:
                message = send_queue.get()
                msg: dict = json.loads(message)
                if msg.get("status") == "quit":
                    raise Exception("Closing connection")
            else:
                message = f'{{"uuid": "{client_uuid}"}}'
            time.sleep(1/70)

    except ConnectionRefusedError:
        print('Connection to the server was refused')

    finally:
        # Close the socket
        client_socket.close()
        print('Connection closed')


def main():
    q = queue.Queue()
    get_message_th = threading.Thread(target=read_messages, args=(q,))
    send_message_th = threading.Thread(target=run_client, args=(q,))
    get_message_th.start()
    send_message_th.start()


if __name__ == '__main__':
    main()
