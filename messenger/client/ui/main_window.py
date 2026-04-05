"""Main application window for LAN Messenger."""

import base64
import os
import tempfile
from collections import defaultdict
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from messenger.client.config import save_config
from messenger.client.network import NetworkClient
from messenger.client.ui.chat_widget import ChatWidget
from messenger.client.ui.sidebar_widget import SidebarWidget
from messenger.client.ui.styles import MAIN_STYLE


class MainWindow(QMainWindow):
    def __init__(self, network: NetworkClient, user_name: str, parent=None):
        super().__init__(parent)
        self.network = network
        self.user_name = user_name
        self.client_id = None

        self.current_room_id = "lobby"
        self.current_room_name = "로비"
        self.joined_rooms = {"lobby"}
        self.all_rooms = []
        self.online_users = []

        # Store chat history per room
        self.chat_histories = defaultdict(list)
        # Store file transfers
        self.file_buffers = {}  # file_id -> {chunks: {}, filename, size, room_id, sender_name}

        self.setWindowTitle("LAN 메신저")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        self.setStyleSheet(MAIN_STYLE)

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarWidget()
        main_layout.addWidget(self.sidebar)

        # Right panel
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(0)

        # Chat header
        header = QWidget()
        header.setObjectName("chat_header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        self.header_label = QLabel(self.current_room_name)
        self.header_label.setObjectName("chat_header_label")
        self.header_label.setFont(QFont("", 16, QFont.Bold))
        self.member_label = QLabel("")
        self.member_label.setObjectName("chat_member_label")
        header_layout.addWidget(self.header_label)
        header_layout.addWidget(self.member_label)
        right_panel.addWidget(header)

        # Chat area
        self.chat_widget = ChatWidget()
        right_panel.addWidget(self.chat_widget, stretch=1)

        # Input area
        input_container = QWidget()
        input_container.setStyleSheet("background-color: #FFFFFF; border-top: 1px solid #E5E5E5;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 8, 10, 8)
        input_layout.setSpacing(8)

        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("attach_button")
        self.attach_btn.setToolTip("파일 첨부")
        self.attach_btn.clicked.connect(self._on_attach)
        input_layout.addWidget(self.attach_btn)

        self.message_input = QLineEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("메시지를 입력하세요...")
        self.message_input.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.message_input, stretch=1)

        self.send_btn = QPushButton("전송")
        self.send_btn.setObjectName("send_button")
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        right_panel.addWidget(input_container)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget, stretch=1)

    def _setup_menu(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("설정")

        change_name_action = QAction("이름 변경", self)
        change_name_action.triggered.connect(self._on_change_name)
        settings_menu.addAction(change_name_action)

    def _connect_signals(self):
        self.network.hello_ack_received.connect(self._on_hello_ack)
        self.network.message_received.connect(self._on_chat_message)
        self.network.room_updated.connect(self._on_room_update)
        self.network.room_list_received.connect(self._on_room_list)
        self.network.user_list_received.connect(self._on_user_list)
        self.network.system_message.connect(self._on_system_message)
        self.network.file_offer_received.connect(self._on_file_offer)
        self.network.file_chunk_received.connect(self._on_file_chunk)
        self.network.file_done_received.connect(self._on_file_done)
        self.network.disconnected.connect(self._on_disconnected)

        self.sidebar.room_selected.connect(self._on_room_selected)
        self.sidebar.create_room_requested.connect(self._on_create_room)
        self.sidebar.join_room_requested.connect(self._on_join_room)
        self.sidebar.leave_room_requested.connect(self._on_leave_room)

    # --- Network event handlers ---

    def _on_hello_ack(self, msg: dict):
        self.client_id = msg.get("client_id")
        rooms = msg.get("rooms", [])
        self.all_rooms = rooms
        self.sidebar.update_rooms(rooms, self.joined_rooms)

    def _on_chat_message(self, msg: dict):
        room_id = msg.get("room_id")
        sender_name = msg.get("sender_name", "")
        text = msg.get("text", "")
        timestamp = msg.get("timestamp", datetime.now().strftime("%H:%M"))
        sender_id = msg.get("sender_id", "")
        is_mine = sender_id == self.client_id

        entry = {
            "type": "chat",
            "sender_name": sender_name,
            "text": text,
            "timestamp": timestamp,
            "is_mine": is_mine,
        }
        self.chat_histories[room_id].append(entry)

        if room_id == self.current_room_id:
            self.chat_widget.add_message(sender_name, text, timestamp, is_mine)

    def _on_room_update(self, msg: dict):
        room_id = msg.get("room_id")
        room_name = msg.get("room_name", "")
        members = msg.get("members", [])

        # Update room in all_rooms list
        found = False
        for r in self.all_rooms:
            if r["room_id"] == room_id:
                r["name"] = room_name
                r["member_count"] = len(members)
                found = True
                break
        if not found:
            self.all_rooms.append({
                "room_id": room_id,
                "name": room_name,
                "member_count": len(members),
                "is_default": False,
            })

        # Check if I'm a member
        my_ids = {self.client_id}
        for m in members:
            if m.get("client_id") == self.client_id:
                self.joined_rooms.add(room_id)
                break

        self.sidebar.update_rooms(self.all_rooms, self.joined_rooms)

        if room_id == self.current_room_id:
            names = [m["name"] for m in members]
            self.member_label.setText(f"참여자: {', '.join(names)}")

    def _on_room_list(self, rooms: list):
        self.all_rooms = rooms
        self.sidebar.update_rooms(rooms, self.joined_rooms)

    def _on_user_list(self, users: list):
        self.online_users = users
        self.sidebar.update_users(users)

    def _on_system_message(self, msg: dict):
        room_id = msg.get("room_id")
        text = msg.get("text", "")

        entry = {"type": "system", "text": text}
        self.chat_histories[room_id].append(entry)

        if room_id == self.current_room_id:
            self.chat_widget.add_system_message(text)

    def _on_file_offer(self, msg: dict):
        file_id = msg.get("file_id")
        room_id = msg.get("room_id")
        filename = msg.get("filename", "file")
        file_size = msg.get("file_size", 0)
        sender_name = msg.get("sender_name", "")
        sender_id = msg.get("sender_id", "")
        is_mine = sender_id == self.client_id

        self.file_buffers[file_id] = {
            "chunks": {},
            "filename": filename,
            "file_size": file_size,
            "room_id": room_id,
            "sender_name": sender_name,
            "sender_id": sender_id,
        }

        size_str = self._format_size(file_size)
        text = f"{filename} ({size_str})"
        timestamp = datetime.now().strftime("%H:%M")

        entry = {
            "type": "chat",
            "sender_name": sender_name,
            "text": f"[파일] {text}",
            "timestamp": timestamp,
            "is_mine": is_mine,
            "is_file": True,
        }
        self.chat_histories[room_id].append(entry)

        if room_id == self.current_room_id:
            self.chat_widget.add_message(
                sender_name, text, timestamp, is_mine, is_file=True
            )

    def _on_file_chunk(self, msg: dict):
        file_id = msg.get("file_id")
        chunk_index = msg.get("chunk_index", 0)
        data = msg.get("data", "")

        if file_id in self.file_buffers:
            self.file_buffers[file_id]["chunks"][chunk_index] = data

    def _on_file_done(self, msg: dict):
        file_id = msg.get("file_id")
        sender_id = msg.get("sender_id", "")

        if file_id not in self.file_buffers:
            return

        buf = self.file_buffers[file_id]

        # Don't save files I sent myself
        if sender_id == self.client_id:
            del self.file_buffers[file_id]
            return

        # Reassemble file
        chunks = buf["chunks"]
        filename = buf["filename"]

        # Ask where to save
        save_path, _ = QFileDialog.getSaveFileName(
            self, "파일 저장", filename
        )
        if save_path:
            try:
                with open(save_path, "wb") as f:
                    for i in sorted(chunks.keys()):
                        f.write(base64.b64decode(chunks[i]))
                room_id = buf["room_id"]
                self.chat_histories[room_id].append({
                    "type": "system",
                    "text": f"파일 저장 완료: {save_path}",
                })
                if room_id == self.current_room_id:
                    self.chat_widget.add_system_message(f"파일 저장 완료: {os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"파일 저장 실패: {e}")

        del self.file_buffers[file_id]

    def _on_disconnected(self):
        self.chat_widget.add_system_message("서버와의 연결이 끊어졌습니다.")
        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)

    # --- UI event handlers ---

    def _on_send(self):
        text = self.message_input.text().strip()
        if not text:
            return
        if self.current_room_id not in self.joined_rooms:
            QMessageBox.information(self, "알림", "먼저 채팅방에 참여해주세요.")
            return
        self.network.send_chat(self.current_room_id, text)
        self.message_input.clear()

    def _on_attach(self):
        if self.current_room_id not in self.joined_rooms:
            QMessageBox.information(self, "알림", "먼저 채팅방에 참여해주세요.")
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if file_path:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                QMessageBox.warning(self, "알림", "50MB 이하의 파일만 전송할 수 있습니다.")
                return
            self.network.send_file(self.current_room_id, file_path)

    def _on_room_selected(self, room_id: str, room_name: str):
        self.current_room_id = room_id
        self.current_room_name = room_name
        self.sidebar.set_current_room(room_id)
        self.header_label.setText(room_name)

        # Reload chat history for this room
        self.chat_widget.clear_messages()
        for entry in self.chat_histories.get(room_id, []):
            if entry["type"] == "system":
                self.chat_widget.add_system_message(entry["text"])
            else:
                self.chat_widget.add_message(
                    entry["sender_name"],
                    entry["text"],
                    entry["timestamp"],
                    entry["is_mine"],
                    entry.get("is_file", False),
                )

    def _on_create_room(self, room_name: str):
        self.network.create_room(room_name)

    def _on_join_room(self, room_id: str):
        self.network.join_room(room_id)
        self.joined_rooms.add(room_id)

    def _on_leave_room(self, room_id: str):
        self.network.leave_room(room_id)
        self.joined_rooms.discard(room_id)
        if self.current_room_id == room_id:
            self._on_room_selected("lobby", "로비")

    def _on_change_name(self):
        new_name, ok = QInputDialog.getText(
            self, "이름 변경", "새 이름:", text=self.user_name
        )
        if ok and new_name.strip():
            new_name = new_name.strip()
            self.user_name = new_name
            self.network.change_name(new_name)
            save_config(name=new_name)
            self.setWindowTitle(f"LAN 메신저 - {new_name}")

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def closeEvent(self, event):
        self.network.disconnect()
        event.accept()
