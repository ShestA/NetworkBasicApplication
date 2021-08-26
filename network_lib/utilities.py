import json
import socket
from time import sleep
import logging


def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


def pack_data(data, seq, ack=0, fin=0, block_size=1024):
    data = {"HEADER": {"DATA_LENGTH": len(data), "SEQ": seq, "ACK": ack, "FIN": fin}, "DATA": data}
    data = json.dumps(data).encode("utf-8")
    data += b" " * (block_size - len(data))
    return data


def get_data(connection, block_size=1024, retries=200):
    n = 0
    while n < retries:
        n = n + 1
        try:
            data = connection.recv(block_size, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                continue
            else:
                data = json.loads(data.decode("utf-8"))
                connection.recv(block_size)
                # error on python<3.10 garbage collector deleted "open"
                # logging.debug(f"Received from {connection}: {data}")
                return data
        except BlockingIOError:
            sleep(0.1)
            continue
        except ConnectionResetError:
            return None
        except ConnectionRefusedError:
            return None
        except BrokenPipeError:
            return None
    return None


def send_data(connection, data, retries=200):
    n = 0
    res = False
    # logging.debug(f"Sending by {connection}, data={data.decode('utf-8').replace(' ', '')}")
    while n < retries:
        try:
            connection.sendall(data)
            res = True
            break
        except BlockingIOError:
            sleep(0.1)
            continue
        except ConnectionResetError:
            return False
        except ConnectionRefusedError:
            return None
        except BrokenPipeError:
            return None
    return res
