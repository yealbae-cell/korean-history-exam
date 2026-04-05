"""Chat bubble widget - KakaoTalk style message bubbles."""

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from messenger.client.ui.styles import (
    MY_BUBBLE_COLOR,
    OTHER_BUBBLE_COLOR,
    SENDER_NAME_COLOR,
    SYSTEM_COLOR,
    TIME_COLOR,
)


class ChatBubble(QWidget):
    """A single chat message bubble."""

    def __init__(self, sender_name: str, text: str, timestamp: str,
                 is_mine: bool, is_file: bool = False, parent=None):
        super().__init__(parent)
        self.sender_name = sender_name
        self.text = text
        self.timestamp = timestamp
        self.is_mine = is_mine
        self.is_file = is_file

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(10, 2, 10, 2)
        outer_layout.setSpacing(6)

        if self.is_mine:
            outer_layout.addStretch()

        bubble_container = QVBoxLayout()
        bubble_container.setSpacing(2)

        # Sender name (only for other's messages)
        if not self.is_mine:
            name_label = QLabel(self.sender_name)
            name_label.setFont(QFont("", 11))
            name_label.setStyleSheet(f"color: {SENDER_NAME_COLOR}; background: transparent; padding: 0px 5px;")
            bubble_container.addWidget(name_label)

        # Bubble + timestamp row
        msg_row = QHBoxLayout()
        msg_row.setSpacing(5)

        # The bubble itself
        bubble = BubbleLabel(self.text, self.is_mine, self.is_file)

        # Timestamp
        time_label = QLabel(self.timestamp or "")
        time_label.setFont(QFont("", 9))
        time_label.setStyleSheet(f"color: {TIME_COLOR}; background: transparent;")
        time_label.setAlignment(Qt.AlignBottom)

        if self.is_mine:
            msg_row.addStretch()
            msg_row.addWidget(time_label)
            msg_row.addWidget(bubble)
        else:
            msg_row.addWidget(bubble)
            msg_row.addWidget(time_label)
            msg_row.addStretch()

        bubble_container.addLayout(msg_row)
        outer_layout.addLayout(bubble_container)

        if not self.is_mine:
            outer_layout.addStretch()


class BubbleLabel(QWidget):
    """The actual rounded-rectangle bubble containing the message text."""

    def __init__(self, text: str, is_mine: bool, is_file: bool = False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_mine = is_mine
        self.is_file = is_file
        self.bg_color = QColor(MY_BUBBLE_COLOR if is_mine else OTHER_BUBBLE_COLOR)
        self.text_color = QColor("#1E1E1E")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMaximumWidth(350)

        # Internal label for text wrapping
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        prefix = "📎 " if is_file else ""
        self.label = QLabel(prefix + text)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("", 13))
        self.label.setStyleSheet(f"color: {self.text_color.name()}; background: transparent;")
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_color)

        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        radius = 15.0

        path.addRoundedRect(rect, radius, radius)

        # Add triangle pointer
        if self.is_mine:
            # Right side triangle
            tri = QPainterPath()
            x = rect.right()
            y = rect.top() + 15
            tri.moveTo(x - 5, y)
            tri.lineTo(x + 5, y + 5)
            tri.lineTo(x - 5, y + 10)
            path = path.united(tri)
        else:
            # Left side triangle
            tri = QPainterPath()
            x = rect.left()
            y = rect.top() + 15
            tri.moveTo(x + 5, y)
            tri.lineTo(x - 5, y + 5)
            tri.lineTo(x + 5, y + 10)
            path = path.united(tri)

        painter.drawPath(path)
        painter.end()


class SystemMessage(QWidget):
    """System notification message (join/leave/name change)."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        label = QLabel(text)
        label.setFont(QFont("", 11))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: #FFFFFF;
            background-color: {SYSTEM_COLOR};
            border-radius: 12px;
            padding: 5px 15px;
        """)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
