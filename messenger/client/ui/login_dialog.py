"""Login dialog for first-time name entry and server connection."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)

from messenger.shared.constants import DEFAULT_PORT


class LoginDialog(QDialog):
    def __init__(self, saved_name: str = "", saved_ip: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("LAN 메신저 - 로그인")
        self.setFixedSize(420, 380)
        self.setStyleSheet("""
            QDialog { background-color: #FEE500; }
            QLabel { color: #3C1E1E; }
            QLineEdit {
                border: 2px solid #E5D300;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus { border-color: #3C1E1E; }
            QPushButton#login_btn {
                background-color: #3C1E1E;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#login_btn:hover { background-color: #5A3535; }
            QRadioButton { color: #3C1E1E; font-size: 13px; }
            QSpinBox {
                border: 2px solid #E5D300;
                border-radius: 8px;
                padding: 5px;
                background: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 25, 30, 25)

        # Title
        title = QLabel("💬 LAN 메신저")
        title.setFont(QFont("", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # Name input
        layout.addWidget(QLabel("이름"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("사용할 이름을 입력하세요")
        self.name_input.setText(saved_name)
        layout.addWidget(self.name_input)

        layout.addSpacing(5)

        # Server mode
        self.server_radio = QRadioButton("서버로 시작 (다른 사람이 접속)")
        self.client_radio = QRadioButton("클라이언트로 접속")
        self.server_radio.setChecked(True)
        layout.addWidget(self.server_radio)
        layout.addWidget(self.client_radio)

        # Server IP input (for client mode)
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("서버 IP:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("예: 192.168.0.10")
        self.ip_input.setText(saved_ip)
        ip_layout.addWidget(self.ip_input)
        ip_layout.addWidget(QLabel("포트:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(DEFAULT_PORT)
        ip_layout.addWidget(self.port_input)
        layout.addLayout(ip_layout)

        self.client_radio.toggled.connect(
            lambda checked: self.ip_input.setEnabled(checked)
        )
        self.ip_input.setEnabled(False)

        layout.addSpacing(10)

        # Login button
        self.login_btn = QPushButton("시작하기")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

        self.result_data = None
        self.name_input.setFocus()

    def _on_login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "알림", "이름을 입력해주세요.")
            return

        is_server = self.server_radio.isChecked()
        server_ip = self.ip_input.text().strip() if not is_server else ""
        port = self.port_input.value()

        if not is_server and not server_ip:
            QMessageBox.warning(self, "알림", "서버 IP를 입력해주세요.")
            return

        self.result_data = {
            "name": name,
            "is_server": is_server,
            "server_ip": server_ip,
            "port": port,
        }
        self.accept()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_login()
        else:
            super().keyPressEvent(event)
