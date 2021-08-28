import logging
from client import Client


logging.basicConfig(filename='client.log', level=logging.DEBUG)


if __name__ == "__main__":
    print("Startup")
    client = Client()
    try:
        client.connect(('localhost', 8080))
        while True:
            try:
                ...
            except KeyboardInterrupt:
                break
    except ConnectionRefusedError as e:
        print(e.strerror)
    print("Cleaning up")
    try:
        client.stop()
        del client
    except Exception as e:
        print(e)
