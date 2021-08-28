import socket
from typing import Union, List
from math import ceil
from time import sleep
# import logging

from .package import Package, PackageType, MetaPackage


def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


def pack_data(package_type: PackageType, data: bytearray, block_size=1024):
    block_number: int
    if len(data) != 0:
        blocks_number = ceil(len(data) / block_size)
    else:
        blocks_number = 1
    blocks = list()
    for block_number in range(blocks_number):
        begin = block_number * block_size
        end = (block_number + 1) * block_size
        package = Package(package_type, block_number, False, blocks_number, data[begin:end])
        package = package.serialize()
        meta = MetaPackage(len(package))
        blocks.append({"meta": meta.raw, "general": package})
    return blocks


def receive_bytes(connection: socket, size: int, retries=10) -> Union[bytearray, None]:
    for _ in range(retries):
        try:
            data = connection.recv(size, socket.MSG_PEEK)
            if len(data) == 0:
                continue
            else:
                connection.recv(size)
                return data
        except BlockingIOError:
            sleep(0.1)
            continue
    raise ConnectionError


def send_bytes(connection: socket, data: bytes, retries=10):
    res = False
    for _ in range(retries):
        try:
            connection.sendall(data)
            res = True
            break
        except BlockingIOError:
            sleep(0.1)
            continue
    return res


def confirm(connection: socket, package: Package, retries=10):
    packages = pack_data(PackageType.ACK, bytearray(str(package.header.seq), "utf-8"))
    package = packages[0]
    meta = package["meta"]
    data = package["general"]
    if not send_bytes(connection, meta, retries):
        return False
    if not send_bytes(connection, data, retries):
        return False
    return True


def get_packages(connection: socket, confirmation=True, retries=10) -> Union[List[Package], None]:
    packages: list[Package]
    packages = []
    errors = 0
    while True:
        meta = receive_bytes(connection, MetaPackage.fixed_size)
        if meta is None:
            return None
        meta = MetaPackage.fromRaw(meta)
        data = receive_bytes(connection, meta.size)
        if data is None:
            errors = errors + 1
            if errors == retries:
                return None
            continue
        package = Package.fromRaw(data)
        packages.append(package)
        if package.header.fin == len(packages):
            break
    if confirmation:
        for package in packages:
            confirm(connection, package)
    if len(packages) == 0:
        return None
    return packages


def get_data(connection: socket, confirmation=True, retries=10) -> Union[bytearray, None]:
    packages = get_packages(connection, confirmation, retries)
    data: bytearray
    data = bytearray()
    for package in packages:
        data.append(package.data)
    return data


def wait_confirmations(connection: socket, packages, retries=10):
    errors = 0
    goods = 0
    while True:
        if errors == retries:
            break
        confirmation = get_data(connection, False)
        if confirmation is None:
            errors = errors + 1
            continue
        seq = int(confirmation.decode("utf-8"))
        for package in packages:
            if package.header.seq == seq:
                package.header.ack = True
                goods = goods + 1
                break
        if goods == len(packages):
            break
    return packages


def send_data(connection: socket, packages, confirmation=True, retries=10):  #: list[dict[str, bytes]]
    corruptions = []
    for package in packages:
        meta = package["meta"]
        data = package["general"]
        if not send_bytes(connection, meta, retries):
            corruptions.append(package)
        if not send_bytes(connection, data, retries):
            corruptions.append(package)
    if confirmation:
        packages = wait_confirmations(connection, packages)
        for package in packages:
            if not package.header.ack:
                corruptions.append(package)
    return corruptions
