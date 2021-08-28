import enum
import pickle


class PackageType(enum.Enum):
    SYN = enum.auto()
    SYN_ACK = enum.auto()
    ACK = enum.auto()
    DATA = enum.auto()
    FIN = enum.auto()


class Header:
    def __init__(self, package_type: PackageType, seq: int, ack: bool, fin: int, size: int):
        self.__type = package_type
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

    @ack.setter
    def ack(self, ack):
        self.__ack = ack

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


def __decompress__(data: bytearray):
    return data


class Package:

    def __init__(self, package_type: PackageType, seq: int, ack: bool, fin: int, data: bytearray, compress=True):
        self.__data: bytearray
        if compress:
            self.__data = __compress__(data)
        else:
            self.__data = data
        self.__header = Header(package_type, seq, ack, fin, len(self.__data))

    def __del__(self):
        ...

    @classmethod
    def fromPackage(cls, package):
        header = package.header
        raw_data = package.raw_data
        type = header.type
        seq = header.seq
        ack = header.ack
        fin = header.fin
        return cls(type, seq, ack, fin, raw_data, False)

    @classmethod
    def fromRaw(cls, raw: bytes):
        package = pickle.loads(raw)
        return cls.fromPackage(package)

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
        return __decompress__(self.__data)

    @property
    def raw_data(self):
        return self.__data


class MetaPackage:
    fixed_size = 64

    def __init__(self, size: int):
        self.__size = size.to_bytes(MetaPackage.fixed_size, "big")

    @classmethod
    def fromRaw(cls, raw: bytes):
        return cls(int.from_bytes(raw, "big"))

    @property
    def raw(self):
        return self.__size

    @raw.getter
    def raw(self):
        return self.__size

    @property
    def size(self):
        return self.__size

    @size.getter
    def size(self):
        return int.from_bytes(self.__size, "big")
