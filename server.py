import socket
import json
import threading

from clsClient import Client


def receive(client: Client):
    str_data = client.skt.recv(1024).decode()
    if not str_data:
        return False
    if "{" in str_data:
        return json.loads(str_data)
    return str_data


def receive_and_respond(client: Client, response):
    str_data = client.skt.recv(1024).decode()
    client.skt.sendall(response.encode())
    print(f"{str_data=}")
    return json.loads(str_data)


def handle_client(client: Client, clients: list[Client]):
    response = f'{{"config":"{client}"}}\n'
    resp_dict = receive_and_respond(client, response)
    client.config(resp_dict)
    # print(client.skt.send("whatever".encode()))
    # client.skt.sendall(response.encode())
    try:
        while True:
            data = receive(client)
            if data is False:
                break

            # print('Received message from {}: {}'.format(client.address, data))
            if data != 'none':
                for other in clients:
                    if other is not client:
                        other.put_mess(data)

            # Send a response to the client
            response = {"new_mess": client.get_all()}
            print(response)
            client.skt.sendall(f"{json.dumps(response)}\n".encode())

    except Exception as e:
        print(f'Error occurred with client {client}: {e}')

    finally:
        # Close the client socket connection
        client.skt.close()
        print('Connection closed with {}:{}'.format(*client.address))


def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 5050

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(10)
    print('Server listening on {}:{}'.format(host, port))

    clients = []

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        client = Client(client_socket, client_address)
        clients.append(client)
        print('Accepted connection from {}:{}'.format(*client_address))
        client_thread = threading.Thread(target=handle_client, args=(client, clients))
        client_thread.start()


    # Close the server socket
    # server_socket.close()


if __name__ == '__main__':
    main()