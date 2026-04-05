"""Chat area widget - scrollable area containing message bubbles."""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from messenger.client.ui.bubble_widget import ChatBubble, SystemMessage
from messenger.client.ui.styles import CHAT_BG_COLOR


class ChatWidget(QScrollArea):
    """Scrollable chat area with message bubbles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_area")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"background-color: {CHAT_BG_COLOR}; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {CHAT_BG_COLOR};")
        self.layout_ = QVBoxLayout(self.container)
        self.layout_.setSpacing(4)
        self.layout_.setContentsMargins(5, 10, 5, 10)
        self.layout_.addStretch()

        self.setWidget(self.container)

    def add_message(self, sender_name: str, text: str, timestamp: str,
                    is_mine: bool, is_file: bool = False):
        bubble = ChatBubble(sender_name, text, timestamp, is_mine, is_file)
        self.layout_.insertWidget(self.layout_.count() - 1, bubble)
        self._scroll_to_bottom()

    def add_system_message(self, text: str):
        msg = SystemMessage(text)
        self.layout_.insertWidget(self.layout_.count() - 1, msg)
        self._scroll_to_bottom()

    def clear_messages(self):
        while self.layout_.count() > 1:  # Keep the stretch
            item = self.layout_.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))
