import asyncio
from typing import List
from ISocket.ISocket import ISocketServer, ISocketClient


class Node:
    """P2P node that contains both server and client functionality."""
    def __init__(self, port: int) -> None:
        self._loop = asyncio.get_event_loop()
        self._server = ISocketServer(self._loop, port)
        self._clients: List[ISocketClient] = []

    async def start_server(self) -> None:
        """Start server and listen for incoming connections."""
        await self._server.main_loop()

    async def connect_to_peer(self, address: str, port: int) -> None:
        """Connect to another peer node."""
        client = ISocketClient(self._loop, address, port)
        # TODO: Accessing protected member _is_connected
        if client._is_connected:
            self._clients.append(client)
            asyncio.create_task(client.main_loop())

    async def broadcast_message(self, message: str) -> None:
        """Send message to all connected peers."""
        for client in self._clients:
            await client.send(message)

    async def close(self) -> None:
        """Shutdown node and close all connections."""
        for client in self._clients:
            await client.close()
        await self._server.close()


class NodeManager:
    """Manager class for handling multiple nodes."""
    def __init__(self) -> None:
        self._nodes: List[Node] = []
        self._loop = asyncio.get_event_loop()

    async def create_node(self, port: int) -> Node:
        """Create and start a new node."""
        node = Node(port)
        self._nodes.append(node)
        asyncio.create_task(node.start_server())
        return node

    async def connect_nodes(self, node: Node, peer_address: str,
                            peer_port: int) -> None:
        """Establish connection between nodes."""
        await node.connect_to_peer(peer_address, peer_port)

    async def shutdown(self) -> None:
        """Shutdown all nodes."""
        for node in self._nodes:
            await node.close()


async def main():
    """Example usage of the P2P network."""
    manager = NodeManager()

    # Create two nodes
    node1 = await manager.create_node(8001)
    # TODO: Unused variable node2
    await manager.create_node(8002)

    # Connect node1 to node2
    await manager.connect_nodes(node1, "127.0.0.1", 8002)

    # Example message broadcast
    await node1.broadcast_message("Hello from node1!")

    try:
        # Keep the program running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
