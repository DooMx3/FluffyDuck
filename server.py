import socket
import json
import threading
from random import randint, choice

from clsClient import Client
from resources import *

BYTES = 4 * 1024


def generate_map():
    x = 300
    poles_amount = 25
    poles = []
    potions = []
    for _ in range(poles_amount):
        y = randint(185, 585)
        poles.append((x, y, randint(190, 240)))
        addx = randint(250, 300)
        x += addx
        if randint(1, 6) == 2:
            potion_y = randint(10, 560)
            potions.append((choice((Potion.BOOST, Potion.PEN)), x - (addx // 2 - 30), potion_y))
    fline = x + 400
    return {"poles": poles, "potions": potions, "fline": fline}


def receive(client: Client):
    str_data = client.skt.recv(BYTES).decode()
    if not str_data:
        return False
    if "{" in str_data:
        return json.loads(str_data)
    return str_data


def receive_and_respond(client: Client, response):
    str_data = client.skt.recv(BYTES).decode()
    client.skt.sendall(response.encode())
    print(f"{str_data=}")
    return json.loads(str_data)


def handle_client(client: Client, clients: list[Client], the_map: dict):
    response = {"the_map": the_map}
    resp_dict = receive_and_respond(client, json.dumps(response))
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
            client.skt.sendall(f"{json.dumps(response)}".encode())

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

    # generating map
    the_map = generate_map()

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        client = Client(client_socket, client_address)
        clients.append(client)
        print('Accepted connection from {}:{}'.format(*client_address))
        client_thread = threading.Thread(target=handle_client, args=(client, clients, the_map))
        client_thread.start()


    # Close the server socket
    # server_socket.close()


if __name__ == '__main__':
    main()
