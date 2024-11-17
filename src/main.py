import socket
from abc import ABC, abstractmethod


class IRemoteNode(ABC):
    def __init__(self):
        self._incoming_requests: list[str] = []

    @abstractmethod
    def _send(self, message: bytes):
        pass

    @abstractmethod
    def _receive(self) -> bytes:
        pass

    def send_response(self, message: str):
        self._send(message.encode())

    def _save_request(self):
        message: bytes = self._receive()
        buffer: bytes = message
        while buffer:
            buffer = self._receive()
            message += buffer
        self._incoming_requests.append(message.decode())

    def get_request(self):
        return self._incoming_requests.pop()


class INodePart(ABC):
    pass


class ISocket(ABC):
    def __init__(self, adress: str, port: int):
        self._adress: str = adress
        self._port: int = port
        self._socket: socket.socket = socket.socket()

    @abstractmethod
    def _connect(self):
        pass

    def __post_init__(self):
        self._connect()

    def __del__(self):
        self._socket.close()


class ClientNodePart(INodePart):
    pass
    # send connection request


class ServerNode(ISocket, IRemoteNode):
    pass


class ServerNodePart(ISocket, INodePart):
    def __init__(self, port: int):
        ISocket.__init__(self, 'localhost', port)

    def _connect(self):
        self._socket.bind(('localhost', self._port))
        self._socket.listen()
    # lisen and aprove


class ClientNode(IRemoteNode):
    pass


class Node:
    def __init__(self, port: int):
        self._serverNodePart: ServerNodePart = ServerNodePart()
        self._clientNodePart: ClientNodePart = ClientNodePart()
