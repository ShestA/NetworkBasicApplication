import logging
from client import Client
from command_controller import CommandController
from network_lib.utilities import ExitException

logging.basicConfig(filename='client.log', level=logging.DEBUG)


if __name__ == "__main__":
    print("Startup")
    client = Client()
    controller = CommandController(client)
    try:
        client.connect(('localhost', 8080))
        while True:
            try:
                controller.run()
            except ExitException:
                print("Stopping")
                break
            except KeyboardInterrupt:
                break
    except ConnectionRefusedError as e:
        print(e.strerror)
    print("Cleaning up")
    client.stop()
    del client
