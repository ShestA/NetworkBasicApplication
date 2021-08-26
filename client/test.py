from time import sleep
import threading
import logging
from client import Client


logging.basicConfig(filename='client.log', encoding='utf-8', level=logging.DEBUG)


def test_sequence_connection(num):
    try:
        for _ in range(num):
            client = Client(('localhost', 8080))
            sleep(1)
            client.stop()
            sleep(1)
    except OSError as e:
        logging.error(e.strerror)


def test_parallel_connections(num):
    threads = []
    for _ in range(num):
        thr = threading.Thread(target=test_sequence_connection)
        thr.start()
        threads.append(thr)
    for thread in threads:
        thread.join()
    sleep(1)


print("Sequence Connection Test")
test_sequence_connection(100)
logging.info("Parallel Connection Test")
test_parallel_connections(100)