import logging
import threading
from network_lib.client import Client

from command_controller import CommandController
from listener_handlers import GoodByeHandler, ReceiveDataHandler

logging.basicConfig(filename='client.log', level=logging.DEBUG)


if __name__ == "__main__":
    print("Startup", flush=True)
    exit_event = threading.Event()
    name = input("What is Your name?\n")
    client = Client(name)
    runner = GoodByeHandler(client)
    receiver = ReceiveDataHandler(client)
    client.registerHandler(runner)
    client.registerHandler(receiver)
    controller = CommandController(client)
    controller.run(exit_event)
    try:
        while True:
            if exit_event.is_set():
                break
    except KeyboardInterrupt:
        ...
    print("Cleaning up", flush=True)
    controller.stop()
    client.stop()
    client.join()
    client.disconnect()
