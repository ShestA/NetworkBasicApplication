import socket
import signal
import threading
from random import randrange
from typing import Union

from common_lib import get_data, pack_data, send_data

active = True


def signal_handler(sig, frame):
    global active
    global main_thread
    active = False
    main_thread.join()
    print("Good bye")


signal.signal(signal.SIGINT, signal_handler)


def welcome_handshake(connection):
    print("Start welcome")
    data = pack_data("USERNAME", 100, 100)
    if not send_data(connection, data):
        print("Can't send message")
    data = get_data(connection)
    print(data)
    if data is None:
        return None
    if data["HEADER"]["ACK"] == 101:
        username = data["DATA"]
        seq = data["HEADER"]["SEQ"] + 1
        ack = data["HEADER"]["ACK"]
        data = pack_data("OK", ack, seq)
        connection.sendall(data)
        return username, seq


def listener(connection, seq):
    data = get_data(connection)
    if data is None:
        return None
    if data["DATA"] == "CLOSE":
        ack = data["HEADER"]["ACK"]
        data = pack_data("OK", ack, seq + 1)
        if not send_data(connection, data):
            print("Can't send message")
        return False
    return True


def good_bye(connection, seq):
    data = pack_data("CLOSE", 100, seq)
    if not send_data(connection, data):
        print("Can't send message")
    data = get_data(connection)
    print(data)
    if data is None:
        return False
    if data["DATA"] == "OK":
        print("Connection closed")
        return True
    return False


def client_handler(connection):
    global active
    username, seq = welcome_handshake(connection)
    if username is not None:
        print(f"New user {username}")
        alive = True
        while active and alive:
            res = listener(connection, seq)
            if res is False:
                break
            elif res is True:
                seq = seq + 1
        if not good_bye(connection, seq):
            print("Connection refused")
    print(f"Closing connection: connection={connection}")
    connection.close()


def acceptor():
    print("Waiting for clients")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
        idx = -1
        connections = {}
        master_socket.bind(('0.0.0.0', 8080))
        master_socket.setblocking(False)
        master_socket.listen()
        while active:
            try:
                connection, _ = master_socket.accept()
                con_id = idx + 1
                idx = con_id
                print(f"New connection {con_id}: connection={connection}")
                connections[con_id] = threading.Thread(target=client_handler, args=(connection,))
                connections[con_id].start()
            except BlockingIOError:
                ...
        for _, connection in connections.items():
            connection.join()
        connections.clear()


main_thread = threading.Thread(target=acceptor)
main_thread.start()
