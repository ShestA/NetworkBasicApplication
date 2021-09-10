import socket
from typing import IO, Union, AnyStr
from subprocess import Popen, PIPE
import os
import fcntl


def setNonBlocking(fd: IO[bytes]):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def capture_output(prefix: str, fd: int) -> Union[str, None]:
    i = 0
    while i < 10000:
        i = i + 1
        try:
            captured_string = os.read(fd, 4096)
            print(f"Captured {prefix}: ", captured_string)
            return captured_string.decode("utf-8")
        except socket.error:
            ...
    return None


def check_output(fd: int, string: str):
    response = os.read(fd, 128)
    assert string in response.decode("utf-8")


def send_string_to_app(app: IO[AnyStr], string: str):
    app.write(string.encode("utf-8"))
    app.flush()


def test_client_try_to_connect():
    client_app = Popen(["python3", f"{os.getcwd()}/client/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app_out = client_app.stdout.fileno()
    client_app_in = client_app.stdin
    check_output(client_app_out, "Startup")
    send_string_to_app(client_app_in, "Name#1\n")
    check_output(client_app_out, ">>")
    send_string_to_app(client_app_in, "connect 127.0.0.1:8080\n")
    check_output(client_app_out, "not available")
    client_app.kill()


def test_client_connect_disconnect():
    server_app = Popen(["python3", f"{os.getcwd()}/server/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app = Popen(["python3", f"{os.getcwd()}/client/main.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    client_app_out = client_app.stdout.fileno()
    client_app_in = client_app.stdin
    check_output(client_app_out, "Startup")
    send_string_to_app(client_app_in, "Name#1\n")
    check_output(client_app_out, ">>")
    send_string_to_app(client_app_in, "connect 127.0.0.1:8080\n")
    check_output(client_app_out, "Welcome")
    send_string_to_app(client_app_in, "disconnect\n")
    check_output(client_app_out, "Good bye\nDisconnected\n>>")
    client_app.kill()
    server_app.kill()


def test_connect_send_disconnect():
    ...
