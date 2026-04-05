"""Sidebar widget - room list and online user list."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class SidebarWidget(QWidget):
    """Left sidebar with room list and online users."""

    room_selected = pyqtSignal(str, str)  # room_id, room_name
    create_room_requested = pyqtSignal(str)  # room_name
    join_room_requested = pyqtSignal(str)  # room_id
    leave_room_requested = pyqtSignal(str)  # room_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self._rooms = []  # [{room_id, name, member_count, is_default, joined}]
        self._users = []
        self._joined_rooms = set()
        self._current_room_id = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title
        title = QLabel("  💬 채팅방")
        title.setObjectName("sidebar_title")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)

        # New room button
        new_room_btn = QPushButton("+ 새 채팅방")
        new_room_btn.setObjectName("new_room_button")
        new_room_btn.clicked.connect(self._on_new_room)
        layout.addWidget(new_room_btn)

        # Room list
        section1 = QLabel("채팅방 목록")
        section1.setObjectName("section_label")
        layout.addWidget(section1)

        self.room_list = QListWidget()
        self.room_list.setObjectName("room_list")
        self.room_list.itemClicked.connect(self._on_room_clicked)
        layout.addWidget(self.room_list, stretch=1)

        # Join / Leave buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 5, 10, 5)
        self.join_btn = QPushButton("참여하기")
        self.join_btn.setObjectName("join_button")
        self.join_btn.clicked.connect(self._on_join)
        self.leave_btn = QPushButton("나가기")
        self.leave_btn.setObjectName("leave_button")
        self.leave_btn.clicked.connect(self._on_leave)
        btn_layout.addWidget(self.join_btn)
        btn_layout.addWidget(self.leave_btn)
        layout.addLayout(btn_layout)

        # Online users
        section2 = QLabel("접속자 목록")
        section2.setObjectName("section_label")
        layout.addWidget(section2)

        self.user_list = QListWidget()
        self.user_list.setObjectName("user_list")
        layout.addWidget(self.user_list, stretch=1)

    def update_rooms(self, rooms: list, joined_rooms: set):
        self._rooms = rooms
        self._joined_rooms = joined_rooms
        self.room_list.clear()
        for room in rooms:
            rid = room["room_id"]
            name = room["name"]
            count = room.get("member_count", 0)
            joined = rid in joined_rooms
            prefix = "● " if joined else "○ "
            item = QListWidgetItem(f"{prefix}{name} ({count}명)")
            item.setData(Qt.UserRole, rid)
            item.setData(Qt.UserRole + 1, name)
            if rid == self._current_room_id:
                item.setSelected(True)
            self.room_list.addItem(item)

    def update_users(self, users: list):
        self._users = users
        self.user_list.clear()
        for user in users:
            self.user_list.addItem(f"🟢 {user['name']}")

    def set_current_room(self, room_id: str):
        self._current_room_id = room_id

    def _on_room_clicked(self, item: QListWidgetItem):
        room_id = item.data(Qt.UserRole)
        room_name = item.data(Qt.UserRole + 1)
        if room_id:
            self._current_room_id = room_id
            self.room_selected.emit(room_id, room_name)

    def _on_new_room(self):
        name, ok = QInputDialog.getText(self, "새 채팅방", "채팅방 이름:")
        if ok and name.strip():
            self.create_room_requested.emit(name.strip())

    def _on_join(self):
        item = self.room_list.currentItem()
        if item:
            room_id = item.data(Qt.UserRole)
            if room_id and room_id not in self._joined_rooms:
                self.join_room_requested.emit(room_id)

    def _on_leave(self):
        item = self.room_list.currentItem()
        if item:
            room_id = item.data(Qt.UserRole)
            if room_id and room_id != "lobby" and room_id in self._joined_rooms:
                self.leave_room_requested.emit(room_id)
