# Async P2P Chat

Simple peer-to-peer chat application built with Python using asyncio for asynchronous network communication.

## Features

- Asynchronous peer-to-peer architecture
- No central server required
- Direct messaging between peers
- Command-line interface
- Automatic peer discovery on local network
- Encrypted messages using TLS

## Requirements

- Python 3.7+
- pytest
- poetry

## Installation


git clone url
cd async-p2p-chat
poetry install


## Usage

1. Start the chat client:

`poetry run python chat.py`

2. Available commands:

`connect <ip:port>` - Connect to a peer
`disconnect <per>` - Disconnect from current peer
`list` - List connected peers
`send <message> <per>` - Send message to a peer
`quit` - Exit application
`help` - Show available commands

## How it works

The application uses asyncio to handle multiple concurrent connections. Each peer acts as both server and client, allowing direct communication between nodes. Messages are encrypted using TLS to ensure security.

Key components:
- Network discovery service
- Async message handler
- Peer connection manager
- Encryption layer

## Project Structure


.
├── chat.py           # Main application file
├── peer.py           # Peer connection handling
├── discovery.py      # Network discovery service
├── crypto.py         # Encryption utilities
├── config.py         # Configuration settings
├── pyproject.toml    # Poetry configuration
└── poetry.lock       # Poetry lock file


## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
