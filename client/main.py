import logging
from network_lib.client import Client
from command_controller import CommandController
from common_lib.exceptions import ExitException

logging.basicConfig(filename='client.log', level=logging.DEBUG)


if __name__ == "__main__":
    print("Startup")
    client = Client()
    controller = CommandController(client)
    while True:
        try:
            controller.run()
        except ExitException:
            print("Stopping")
            break
        except KeyboardInterrupt:
            break
    print("Cleaning up")
    del client
