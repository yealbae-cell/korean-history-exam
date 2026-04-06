"""Wire protocol for LAN Messenger.

Every message is a length-prefixed JSON payload:
  [4 bytes big-endian uint32: payload length][UTF-8 JSON payload]
"""

import json
import struct
import uuid
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    HELLO = "HELLO"
    HELLO_ACK = "HELLO_ACK"
    CHAT = "CHAT"
    FILE_OFFER = "FILE_OFFER"
    FILE_CHUNK = "FILE_CHUNK"
    FILE_DONE = "FILE_DONE"
    JOIN_ROOM = "JOIN_ROOM"
    LEAVE_ROOM = "LEAVE_ROOM"
    CREATE_ROOM = "CREATE_ROOM"
    ROOM_UPDATE = "ROOM_UPDATE"
    ROOM_LIST = "ROOM_LIST"
    USER_LIST = "USER_LIST"
    NAME_CHANGE = "NAME_CHANGE"
    SYSTEM = "SYSTEM"


def make_message(msg_type: MessageType, **kwargs) -> dict:
    return {"type": msg_type.value, "id": str(uuid.uuid4()), **kwargs}


def encode_message(msg: dict) -> bytes:
    payload = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    header = struct.pack("!I", len(payload))
    return header + payload


def decode_header(data: bytes) -> int:
    return struct.unpack("!I", data)[0]


def decode_payload(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))


async def async_read_message(reader) -> dict | None:
    """Read a single length-prefixed message from an asyncio StreamReader."""
    header = await reader.readexactly(4)
    length = decode_header(header)
    if length > 10 * 1024 * 1024:
        raise ValueError(f"Message too large: {length}")
    payload = await reader.readexactly(length)
    return decode_payload(payload)


def sync_read_message(sock) -> dict | None:
    """Read a single length-prefixed message from a blocking socket."""
    header = _recv_exactly(sock, 4)
    if header is None:
        return None
    length = decode_header(header)
    if length > 10 * 1024 * 1024:
        raise ValueError(f"Message too large: {length}")
    payload = _recv_exactly(sock, length)
    if payload is None:
        return None
    return decode_payload(payload)


def _recv_exactly(sock, n: int) -> bytes | None:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data
