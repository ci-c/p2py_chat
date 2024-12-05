import socket
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
import asyncio


class ISocket(ABC):
    """Abstract base class for remote node providing basic message interface."""
    def __init__(self, loop: AbstractEventLoop) -> None:  # asyncio.get_event_loop()
        self._loop: AbstractEventLoop = loop
        self._socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(False)

    @abstractmethod
    async def main_loop(self) -> None:
        """Main message processing loop."""
        pass

    async def close(self) -> None:
        """Close the socket."""
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self._socket.close()


class IEndpointSocket(ISocket):
    """Abstract base class for endpoint socket providing message interface."""
    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__(loop)
        self._is_connected = True

    async def send(self, message: str) -> None:
        """Send message to socket."""  # TODO: Add error handling for encoding
        if self._is_connected:
            try:
                await self._loop.sock_sendall(self._socket, message.encode())
            except (ConnectionError, BrokenPipeError):
                self._is_connected = False
                await self.close()

    async def _receive(self) -> str:
        """Receive data from socket."""  # TODO: Add buffer size limit
        if not self._is_connected:
            return ""
        try:
            data_for_output = b""
            while data := await self._loop.sock_recv(self._socket, 1024):
                data_for_output += data
            return data_for_output.decode()
        except ConnectionError:
            self._is_connected = False
            await self.close()
            return ""

    async def main_loop(self):
        """Main processing loop."""  # TODO: Add timeout handling
        while self._is_connected:
            try:
                data = await self._receive()
                if data:
                    print(f"Received: {data}")
                else:
                    await asyncio.sleep(1)
            except Exception as exc:  # pylint: disable=broad-except
                print(f"Error in main loop: {exc}")
                self._is_connected = False
                await self.close()
                break


class ISocketConnection(IEndpointSocket):
    """Socket connection handler class."""
    def __init__(self, loop: AbstractEventLoop, socket_: socket.socket) -> None:
        # TODO: Potential name shadowing with socket module
        self._loop: AbstractEventLoop = loop
        self._socket = socket_


class ISocketClient(IEndpointSocket):
    """Client socket connection handler."""
    def __init__(self, loop: AbstractEventLoop, server_address: str,
                 port: int) -> None:
        super().__init__(loop)
        try:
            self._socket.connect((server_address, port))
        except ConnectionError:
            self._is_connected = False
            self._socket.close()


class ISocketServer(ISocket):
    """Server socket base class providing message interface."""
    def __init__(self, loop: AbstractEventLoop, port: int) -> None:
        super().__init__(loop)
        self._socket.bind(('127.0.0.1', port))
        self._socket.listen()
        self._connections = set()

    async def main_loop(self) -> None:
        """Main server processing loop."""
        try:
            while True:  # TODO: Add graceful shutdown mechanism
                connection, address = await self._loop.sock_accept(self._socket)
                connection.setblocking(False)
                print(f"Connection request from {address}")
                conn = ISocketConnection(self._loop, connection)
                self._connections.add(conn)
                asyncio.create_task(self._handle_connection(conn, address))
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Server error: {exc}")
            await self.close()

    async def _handle_connection(self, connection: ISocketConnection,
                                 address: tuple) -> None:
        """Handle individual connection."""
        try:
            await connection.main_loop()
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Connection error from {address}: {exc}")
        finally:
            self._connections.remove(connection)
            await connection.close()
            print(f"Connection to {address} closed")

    async def close(self) -> None:
        """Close server and all active connections."""
        for conn in self._connections:
            await conn.close()
        self._connections.clear()
        await super().close()
