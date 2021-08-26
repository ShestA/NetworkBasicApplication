import socket
import select
import threading
import signal
import sys
from random import randrange

from common_lib import get_data, pack_data, send_data

active = True
seq = 100
ack = 100


def signal_handler(sig, frame):
    global active
    global main_thread
    active = False
    main_thread.join()
    print("Good bye")


signal.signal(signal.SIGINT, signal_handler)


def welcome_handshake(connection):
    print("Start welcome")
    global seq
    global ack
    global username
    data = get_data(connection)
    print(data)
    if data is None:
        return False
    if data["DATA"] == "USERNAME":
        seq = data["HEADER"]["SEQ"] + 1
        ack = data["HEADER"]["ACK"]
        data = pack_data(username, ack, seq)
        if not send_data(connection, data):
            print("Can't send message")
        data = get_data(connection)
        print(data)
        if data is None:
            return False
        if data["DATA"] == "OK":
            return True
    return False


def good_bye(connection):
    global seq
    global ack
    data = pack_data("CLOSE", ack, seq)
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


def listener(connection):
    global seq
    global ack
    data = get_data(connection)
    if data is None:
        return None
    if data["DATA"] == "CLOSE":
        ack = data["HEADER"]["ACK"]
        seq = data["HEADER"]["SEQ"] + 1
        data = pack_data("OK", ack, seq)
        if not send_data(connection, data):
            print("Can't send message")
        return False
    return True


def connection_handler():
    global active
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as master_socket:
        master_socket.setblocking(False)
        try:
            status = master_socket.connect(('localhost', 8080))
            if status != 0:
                print("Connection refused")
        except BlockingIOError:
            ...
        except Exception as e:
            print(e)
        print("Connecting...")
        if welcome_handshake(master_socket):
            print("Connected")
            while active:
                if listener(master_socket) is False:
                    print("Connection closed")
                    return
            if not good_bye(master_socket):
                print("Connection refused")
        else:
            print("Connection refused")


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} username")
    sys.exit(0)
username = sys.argv[1]
main_thread = threading.Thread(target=connection_handler)
main_thread.start()
