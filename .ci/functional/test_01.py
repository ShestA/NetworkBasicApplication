import pytest
from subprocess import Popen, PIPE, STDOUT
import os


def test_connect_disconnect():
    s_app = Popen([os.environ['HOME']+"/ServerApp"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    c_app = Popen([os.environ['HOME']+"/ClientApp"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    grep_stdout = c_app.communicate(input=b'connect 127.0.0.1:8080')[0]
    assert grep_stdout == "Server: Welcome"
    c_app.communicate(input=b'send TEST_STRING')
    assert s_app.stdout == "TEST_STRING"
    grep_stdout = c_app.communicate(input=b'disconnect')[0]
    assert grep_stdout == "Server: Good bye\nDisconnected"
    grep_stdout = c_app.communicate(input=b'exit')[0]
    assert grep_stdout == "Stopping\nCleaning up"
    s_app.kill()


def test_connect_send_disconnect():
    ...
