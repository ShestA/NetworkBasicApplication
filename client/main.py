import logging
import threading
from network_lib.client import Client

from command_controller import CommandController
from listener_handlers import GoodByeHandler

logging.basicConfig(filename='client.log', level=logging.DEBUG)


if __name__ == "__main__":
    print("Startup")
    exit_event = threading.Event()
    name = input("What is Your name?\n")
    client = Client(name)
    runner = GoodByeHandler(client)
    client.registerHandler(runner)
    controller = CommandController(client)
    controller.run(exit_event)
    try:
        while True:
            if exit_event.is_set():
                break
    except KeyboardInterrupt:
        ...
    print("Cleaning up")
    controller.stop()
    client.stop()
    client.join()
    client.disconnect()
