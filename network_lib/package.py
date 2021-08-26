import enum
import pickle


class Type(enum.Enum):
    SYN = 1
    SYN_ACK = 2
    ACK = 3
    DATA = 4
    FIN = 5


class Header:
    def __init__(self, type: Type, seq: int, ack: int, fin: int, size: int):
        self.__type = type
        self.__seq = seq
        self.__ack = ack
        self.__fin = fin
        self.__size = size

    def __del__(self):
        ...

    @property
    def type(self):
        return self.__type

    @type.getter
    def type(self):
        return self.__type

    @property
    def seq(self):
        return self.__seq

    @seq.getter
    def seq(self):
        return self.__seq

    @property
    def ack(self):
        return self.__ack

    @ack.getter
    def ack(self):
        return self.__ack

    @property
    def fin(self):
        return self.__fin

    @ack.getter
    def fin(self):
        return self.__fin

    @property
    def size(self):
        return self.__size

    @size.getter
    def size(self):
        return self.__size


def __compress__(data: bytearray):
    return data


class Package:

    def __init__(self, type: Type, seq: int, ack: int, fin: int, data: bytearray):
        self.__data = __compress__(data)
        self.__header = Header(type, seq, ack, fin, len(self.__data))

    def __del__(self):
        ...

    def serialize(self):
        return pickle.dumps(self)

    @property
    def header(self):
        return self.__header

    @header.getter
    def header(self):
        return self.__header

    @property
    def data(self):
        return self.__data

    @data.getter
    def data(self):
        return self.__data
