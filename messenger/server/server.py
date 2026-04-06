"""LAN Messenger Server - TCP server with room management and UDP discovery."""

import asyncio
import json
import logging
import socket
import struct
import uuid
from dataclasses import dataclass, field
from typing import Dict, Set

from messenger.shared.constants import (
    DEFAULT_PORT,
    DISCOVERY_MAGIC,
    DISCOVERY_PORT,
    DISCOVERY_RESPONSE_MAGIC,
)
from messenger.shared.protocol import (
    MessageType,
    async_read_message,
    encode_message,
    make_message,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SERVER] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Client:
    client_id: str
    name: str
    writer: asyncio.StreamWriter
    rooms: Set[str] = field(default_factory=set)


@dataclass
class Room:
    room_id: str
    name: str
    members: Set[str] = field(default_factory=set)
    is_default: bool = False


class MessengerServer:
    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.clients: Dict[str, Client] = {}
        self.rooms: Dict[str, Room] = {}
        self._writer_to_client: Dict[asyncio.StreamWriter, str] = {}

        # Create default lobby room
        lobby_id = "lobby"
        self.rooms[lobby_id] = Room(
            room_id=lobby_id, name="로비", is_default=True
        )

    async def start(self):
        server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        logger.info(f"Server started on {self.host}:{self.port}")

        # Start UDP discovery in background
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._start_udp_discovery_thread)

        async with server:
            await server.serve_forever()

    def _start_udp_discovery_thread(self):
        import threading

        t = threading.Thread(target=self._udp_discovery_loop, daemon=True)
        t.start()

    def _udp_discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", DISCOVERY_PORT))
        except OSError:
            logger.warning(f"Could not bind UDP discovery port {DISCOVERY_PORT}")
            return

        logger.info(f"UDP discovery listening on port {DISCOVERY_PORT}")
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data.startswith(DISCOVERY_MAGIC):
                    response = DISCOVERY_RESPONSE_MAGIC + struct.pack("!H", self.port)
                    sock.sendto(response, addr)
                    logger.info(f"Discovery response sent to {addr}")
            except Exception as e:
                logger.error(f"UDP discovery error: {e}")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        client_id = None
        addr = writer.get_extra_info("peername")
        logger.info(f"New connection from {addr}")

        try:
            # First message must be HELLO
            msg = await async_read_message(reader)
            if not msg or msg.get("type") != MessageType.HELLO:
                writer.close()
                await writer.wait_closed()
                return

            client_id = str(uuid.uuid4())
            client = Client(
                client_id=client_id, name=msg.get("name", "Unknown"), writer=writer
            )
            self.clients[client_id] = client
            self._writer_to_client[writer] = client_id

            # Auto-join lobby
            lobby = self.rooms["lobby"]
            lobby.members.add(client_id)
            client.rooms.add("lobby")

            # Send HELLO_ACK
            ack = make_message(
                MessageType.HELLO_ACK,
                client_id=client_id,
                name=client.name,
                rooms=self._get_room_list(),
            )
            await self._send(writer, ack)

            # Broadcast user list and room update
            await self._broadcast_user_list()
            await self._broadcast_room_update("lobby")

            # Broadcast system message
            await self._broadcast_to_room(
                "lobby",
                make_message(
                    MessageType.SYSTEM,
                    room_id="lobby",
                    text=f"{client.name}님이 입장했습니다.",
                ),
            )

            # Main message loop
            while True:
                msg = await async_read_message(reader)
                if msg is None:
                    break
                await self._dispatch(client_id, msg)

        except (asyncio.IncompleteReadError, ConnectionResetError, ConnectionError):
            pass
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id:
                await self._remove_client(client_id, writer)

    async def _dispatch(self, client_id: str, msg: dict):
        msg_type = msg.get("type")
        client = self.clients.get(client_id)
        if not client:
            return

        if msg_type == MessageType.CHAT:
            room_id = msg.get("room_id")
            if room_id in client.rooms:
                broadcast = make_message(
                    MessageType.CHAT,
                    room_id=room_id,
                    sender_id=client_id,
                    sender_name=client.name,
                    text=msg.get("text", ""),
                    timestamp=msg.get("timestamp"),
                )
                await self._broadcast_to_room(room_id, broadcast)

        elif msg_type == MessageType.FILE_OFFER:
            room_id = msg.get("room_id")
            if room_id in client.rooms:
                broadcast = make_message(
                    MessageType.FILE_OFFER,
                    room_id=room_id,
                    sender_id=client_id,
                    sender_name=client.name,
                    file_id=msg.get("file_id"),
                    filename=msg.get("filename"),
                    file_size=msg.get("file_size"),
                )
                await self._broadcast_to_room(room_id, broadcast)

        elif msg_type == MessageType.FILE_CHUNK:
            room_id = msg.get("room_id")
            if room_id in client.rooms:
                broadcast = make_message(
                    MessageType.FILE_CHUNK,
                    room_id=room_id,
                    file_id=msg.get("file_id"),
                    chunk_index=msg.get("chunk_index"),
                    data=msg.get("data"),
                    sender_id=client_id,
                )
                await self._broadcast_to_room(room_id, broadcast, exclude={client_id})

        elif msg_type == MessageType.FILE_DONE:
            room_id = msg.get("room_id")
            if room_id in client.rooms:
                broadcast = make_message(
                    MessageType.FILE_DONE,
                    room_id=room_id,
                    file_id=msg.get("file_id"),
                    sender_id=client_id,
                )
                await self._broadcast_to_room(room_id, broadcast)

        elif msg_type == MessageType.CREATE_ROOM:
            room_name = msg.get("room_name", "").strip()
            if room_name:
                room_id = str(uuid.uuid4())[:8]
                room = Room(room_id=room_id, name=room_name)
                room.members.add(client_id)
                self.rooms[room_id] = room
                client.rooms.add(room_id)

                # Notify all clients about new room
                await self._broadcast_room_list()
                await self._broadcast_room_update(room_id)
                await self._broadcast_to_room(
                    room_id,
                    make_message(
                        MessageType.SYSTEM,
                        room_id=room_id,
                        text=f"{client.name}님이 방을 만들었습니다.",
                    ),
                )

        elif msg_type == MessageType.JOIN_ROOM:
            room_id = msg.get("room_id")
            if room_id in self.rooms and room_id not in client.rooms:
                self.rooms[room_id].members.add(client_id)
                client.rooms.add(room_id)
                await self._broadcast_room_update(room_id)
                await self._broadcast_to_room(
                    room_id,
                    make_message(
                        MessageType.SYSTEM,
                        room_id=room_id,
                        text=f"{client.name}님이 입장했습니다.",
                    ),
                )

        elif msg_type == MessageType.LEAVE_ROOM:
            room_id = msg.get("room_id")
            if room_id in client.rooms and room_id != "lobby":
                await self._broadcast_to_room(
                    room_id,
                    make_message(
                        MessageType.SYSTEM,
                        room_id=room_id,
                        text=f"{client.name}님이 퇴장했습니다.",
                    ),
                )
                self.rooms[room_id].members.discard(client_id)
                client.rooms.discard(room_id)
                await self._broadcast_room_update(room_id)

                # Remove empty non-default rooms
                room = self.rooms[room_id]
                if not room.members and not room.is_default:
                    del self.rooms[room_id]
                    await self._broadcast_room_list()

        elif msg_type == MessageType.NAME_CHANGE:
            old_name = client.name
            new_name = msg.get("name", "").strip()
            if new_name:
                client.name = new_name
                await self._broadcast_user_list()
                for room_id in client.rooms:
                    await self._broadcast_to_room(
                        room_id,
                        make_message(
                            MessageType.SYSTEM,
                            room_id=room_id,
                            text=f"{old_name}님이 이름을 {new_name}(으)로 변경했습니다.",
                        ),
                    )

    async def _remove_client(self, client_id: str, writer: asyncio.StreamWriter):
        client = self.clients.pop(client_id, None)
        self._writer_to_client.pop(writer, None)
        if not client:
            return

        logger.info(f"Client disconnected: {client.name}")

        for room_id in list(client.rooms):
            room = self.rooms.get(room_id)
            if room:
                room.members.discard(client_id)
                await self._broadcast_to_room(
                    room_id,
                    make_message(
                        MessageType.SYSTEM,
                        room_id=room_id,
                        text=f"{client.name}님이 퇴장했습니다.",
                    ),
                )
                await self._broadcast_room_update(room_id)
                if not room.members and not room.is_default:
                    del self.rooms[room_id]

        await self._broadcast_user_list()
        await self._broadcast_room_list()

        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

    async def _send(self, writer: asyncio.StreamWriter, msg: dict):
        try:
            writer.write(encode_message(msg))
            await writer.drain()
        except Exception:
            pass

    async def _broadcast_to_room(
        self, room_id: str, msg: dict, exclude: set = None
    ):
        room = self.rooms.get(room_id)
        if not room:
            return
        exclude = exclude or set()
        for member_id in room.members:
            if member_id in exclude:
                continue
            client = self.clients.get(member_id)
            if client:
                await self._send(client.writer, msg)

    async def _broadcast_all(self, msg: dict):
        for client in self.clients.values():
            await self._send(client.writer, msg)

    async def _broadcast_user_list(self):
        users = [
            {"client_id": c.client_id, "name": c.name}
            for c in self.clients.values()
        ]
        msg = make_message(MessageType.USER_LIST, users=users)
        await self._broadcast_all(msg)

    async def _broadcast_room_list(self):
        msg = make_message(MessageType.ROOM_LIST, rooms=self._get_room_list())
        await self._broadcast_all(msg)

    async def _broadcast_room_update(self, room_id: str):
        room = self.rooms.get(room_id)
        if not room:
            return
        members = []
        for mid in room.members:
            c = self.clients.get(mid)
            if c:
                members.append({"client_id": c.client_id, "name": c.name})
        msg = make_message(
            MessageType.ROOM_UPDATE,
            room_id=room_id,
            room_name=room.name,
            members=members,
        )
        await self._broadcast_all(msg)

    def _get_room_list(self) -> list:
        return [
            {
                "room_id": r.room_id,
                "name": r.name,
                "member_count": len(r.members),
                "is_default": r.is_default,
            }
            for r in self.rooms.values()
        ]


def run_server(host: str = "0.0.0.0", port: int = DEFAULT_PORT):
    server = MessengerServer(host, port)
    asyncio.run(server.start())


if __name__ == "__main__":
    run_server()
