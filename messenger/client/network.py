"""Network client for LAN Messenger - threaded TCP client with PyQt signal bridge."""

import base64
import os
import socket
import struct
import threading
import time
import uuid
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from messenger.shared.constants import (
    DEFAULT_PORT,
    DISCOVERY_MAGIC,
    DISCOVERY_PORT,
    DISCOVERY_RESPONSE_MAGIC,
    FILE_CHUNK_SIZE,
)
from messenger.shared.protocol import (
    MessageType,
    encode_message,
    make_message,
    sync_read_message,
)


class NetworkClient(QObject):
    """Threaded TCP client that bridges network events to PyQt signals."""

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_failed = pyqtSignal(str)
    message_received = pyqtSignal(dict)
    room_updated = pyqtSignal(dict)
    room_list_received = pyqtSignal(list)
    user_list_received = pyqtSignal(list)
    system_message = pyqtSignal(dict)
    file_offer_received = pyqtSignal(dict)
    file_chunk_received = pyqtSignal(dict)
    file_done_received = pyqtSignal(dict)
    hello_ack_received = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sock = None
        self.client_id = None
        self.name = ""
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def connect_to_server(self, host: str, port: int, name: str):
        self.name = name
        self._running = True
        self._thread = threading.Thread(
            target=self._run, args=(host, port, name), daemon=True
        )
        self._thread.start()

    def disconnect(self):
        self._running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None

    def _run(self, host: str, port: int, name: str):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((host, port))
            self.sock.settimeout(None)
        except Exception as e:
            self.connection_failed.emit(f"연결 실패: {e}")
            return

        # Send HELLO
        hello = make_message(MessageType.HELLO, name=name)
        self._send(hello)
        self.connected.emit()

        # Read loop
        while self._running:
            try:
                msg = sync_read_message(self.sock)
                if msg is None:
                    break
                self._handle_message(msg)
            except Exception:
                break

        self._running = False
        self.disconnected.emit()

    def _handle_message(self, msg: dict):
        msg_type = msg.get("type")
        if msg_type == MessageType.HELLO_ACK:
            self.client_id = msg.get("client_id")
            self.hello_ack_received.emit(msg)
        elif msg_type == MessageType.CHAT:
            self.message_received.emit(msg)
        elif msg_type == MessageType.ROOM_UPDATE:
            self.room_updated.emit(msg)
        elif msg_type == MessageType.ROOM_LIST:
            self.room_list_received.emit(msg.get("rooms", []))
        elif msg_type == MessageType.USER_LIST:
            self.user_list_received.emit(msg.get("users", []))
        elif msg_type == MessageType.SYSTEM:
            self.system_message.emit(msg)
        elif msg_type == MessageType.FILE_OFFER:
            self.file_offer_received.emit(msg)
        elif msg_type == MessageType.FILE_CHUNK:
            self.file_chunk_received.emit(msg)
        elif msg_type == MessageType.FILE_DONE:
            self.file_done_received.emit(msg)

    def _send(self, msg: dict):
        with self._lock:
            if self.sock:
                try:
                    self.sock.sendall(encode_message(msg))
                except Exception:
                    pass

    def send_chat(self, room_id: str, text: str):
        msg = make_message(
            MessageType.CHAT,
            room_id=room_id,
            text=text,
            timestamp=datetime.now().strftime("%H:%M"),
        )
        self._send(msg)

    def send_file(self, room_id: str, file_path: str):
        """Send file in a background thread."""
        t = threading.Thread(
            target=self._send_file_worker, args=(room_id, file_path), daemon=True
        )
        t.start()

    def _send_file_worker(self, room_id: str, file_path: str):
        file_id = str(uuid.uuid4())[:8]
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Send FILE_OFFER
        offer = make_message(
            MessageType.FILE_OFFER,
            room_id=room_id,
            file_id=file_id,
            filename=filename,
            file_size=file_size,
        )
        self._send(offer)

        # Send chunks
        chunk_index = 0
        with open(file_path, "rb") as f:
            while True:
                data = f.read(FILE_CHUNK_SIZE)
                if not data:
                    break
                chunk = make_message(
                    MessageType.FILE_CHUNK,
                    room_id=room_id,
                    file_id=file_id,
                    chunk_index=chunk_index,
                    data=base64.b64encode(data).decode("ascii"),
                )
                self._send(chunk)
                chunk_index += 1
                time.sleep(0.01)  # Throttle slightly

        # Send FILE_DONE
        done = make_message(
            MessageType.FILE_DONE,
            room_id=room_id,
            file_id=file_id,
        )
        self._send(done)

    def create_room(self, room_name: str):
        msg = make_message(MessageType.CREATE_ROOM, room_name=room_name)
        self._send(msg)

    def join_room(self, room_id: str):
        msg = make_message(MessageType.JOIN_ROOM, room_id=room_id)
        self._send(msg)

    def leave_room(self, room_id: str):
        msg = make_message(MessageType.LEAVE_ROOM, room_id=room_id)
        self._send(msg)

    def change_name(self, new_name: str):
        self.name = new_name
        msg = make_message(MessageType.NAME_CHANGE, name=new_name)
        self._send(msg)

    @staticmethod
    def discover_server(timeout: float = 3.0) -> tuple[str, int] | None:
        """Send UDP broadcast to discover a server on the LAN."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(timeout)
            sock.sendto(DISCOVERY_MAGIC, ("<broadcast>", DISCOVERY_PORT))

            data, addr = sock.recvfrom(1024)
            if data.startswith(DISCOVERY_RESPONSE_MAGIC):
                port = struct.unpack(
                    "!H", data[len(DISCOVERY_RESPONSE_MAGIC) : len(DISCOVERY_RESPONSE_MAGIC) + 2]
                )[0]
                return (addr[0], port)
        except socket.timeout:
            pass
        except Exception:
            pass
        return None
