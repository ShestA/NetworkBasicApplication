import socket
from time import sleep
from typing import IO, Union, AnyStr
from subprocess import Popen, PIPE
import os
import fcntl


def setNonBlocking(fd: Union[int, IO[bytes]]):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def capture_output(fd: int) -> Union[str, None]:
    for _ in range(10):
        sleep(0.1)
        try:
            captured_string = os.read(fd, 32)
            # print(f"Captured: ", captured_string)
            return captured_string.decode("utf-8")
        except socket.error:
            ...
        except OSError as e:
            ...
    return None


def check_output(fd: int, string: str):
    # response = os.read(fd, 32)
    response = capture_output(fd)
    assert response is not None
    assert string in response


def send_string_to_app(app: IO[AnyStr], string: str):
    app.write(string.encode("utf-8"))
    app.flush()


def create_client(name: str):
    client_app = Popen(["stdbuf", "-o0", "python3", f"{os.getcwd()}/client/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app_out = client_app.stdout.fileno()
    client_app_in = client_app.stdin
    check_output(client_app_out, "Startup")
    send_string_to_app(client_app_in, f"{name}\n")
    check_output(client_app_out, ">>")
    return client_app, client_app_out, client_app_in


def connect_client(success: bool, client_app_in, client_app_out):
    send_string_to_app(client_app_in, "connect 127.0.0.1:8080\n")
    if success:
        check_output(client_app_out, "Welcome")
    else:
        check_output(client_app_out, "not available")


def test_client_try_to_connect():
    client_app, client_app_out, client_app_in = create_client("Name#1")
    send_string_to_app(client_app_in, "connect 127.0.0.1:8080\n")
    connect_client(False, client_app_in, client_app_out)
    client_app.kill()


def test_client_connect_disconnect():
    server_app = Popen(["stdbuf", "-o0", "python3", f"{os.getcwd()}/server/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app, client_app_out, client_app_in = create_client("Name#1")
    connect_client(True, client_app_in, client_app_out)
    send_string_to_app(client_app_in, "disconnect\n")
    check_output(client_app_out, "Good bye\nDisconnected\n>>")
    client_app.kill()
    server_app.kill()


def test_connect_send_disconnect():
    server_app = Popen(["stdbuf", "-o0", "python3", f"{os.getcwd()}/server/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app_1, client_app_out_1, client_app_in_1 = create_client("Name#1")
    client_app_2, client_app_out_2, client_app_in_2 = create_client("Name#2")
    setNonBlocking(client_app_out_1)
    setNonBlocking(client_app_out_2)
    setNonBlocking(client_app_in_1)
    setNonBlocking(client_app_in_2)
    connect_client(True, client_app_in_1, client_app_out_1)
    connect_client(True, client_app_in_2, client_app_out_2)
    send_string_to_app(client_app_in_1, "send Name#2 TEST_STRING\n")
    check_output(client_app_out_1, ">>")
    check_output(client_app_out_2, "TEST_STRING")
    client_app_1.kill()
    client_app_2.kill()
    server_app.kill()
