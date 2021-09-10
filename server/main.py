import logging
from server import Server

logging.basicConfig(filename='server.log', level=logging.DEBUG)

if __name__ == "__main__":
    print("Startup", flush=True)
    server = Server(('0.0.0.0', 8080))
    try:
        server.run()
    except KeyboardInterrupt:
        ...
    print("Cleaning up", flush=True)
    server.stop()
    del server
