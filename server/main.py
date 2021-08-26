import logging
from server import Server
import atexit


logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.DEBUG)


def cleanup(server):
    print("Cleaning up")
    server.stop()
    del server


if __name__ == "__main__":
    print("Startup")
    server = Server(('0.0.0.0', 8080))
    atexit.register(cleanup, server)
    try:
        server.run()
    except KeyboardInterrupt:
        ...
