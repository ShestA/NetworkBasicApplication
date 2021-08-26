import logging
from client import Client
import atexit


logging.basicConfig(filename='client.log', encoding='utf-8', level=logging.DEBUG)


def cleanup(client: Client):
    print("Cleaning up")
    try:
        client.stop()
        del client
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print("Startup")
    client = Client()
    atexit.register(cleanup, client)
    try:
        client.connect(('localhost', 8080))
        try:
            while True:
                ...
        except KeyboardInterrupt:
            ...
    except ConnectionRefusedError as e:
        print(e.strerror)
