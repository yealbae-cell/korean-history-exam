"""Entry point for LAN Messenger Client."""

import sys
import os
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMessageBox

from messenger.client.config import load_config, save_config
from messenger.client.network import NetworkClient
from messenger.client.ui.login_dialog import LoginDialog
from messenger.client.ui.main_window import MainWindow
from messenger.shared.constants import DEFAULT_PORT


def start_embedded_server(port: int):
    """Start the server in a background thread."""
    from messenger.server.server import MessengerServer
    import asyncio

    def run():
        server = MessengerServer("0.0.0.0", port)
        asyncio.run(server.start())

    t = threading.Thread(target=run, daemon=True)
    t.start()
    # Give server time to start
    import time
    time.sleep(0.5)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LAN 메신저")

    # Load saved config
    config = load_config()
    saved_name = config.get("name", "")
    saved_ip = config.get("server_ip", "")

    # Show login dialog
    dialog = LoginDialog(saved_name=saved_name, saved_ip=saved_ip)
    if dialog.exec_() != LoginDialog.Accepted:
        sys.exit(0)

    data = dialog.result_data
    name = data["name"]
    is_server = data["is_server"]
    server_ip = data["server_ip"]
    port = data["port"]

    # Save config
    save_config(name=name, server_ip=server_ip, server_port=port)

    # Start embedded server if server mode
    if is_server:
        start_embedded_server(port)
        server_ip = "127.0.0.1"

    # Create network client
    network = NetworkClient()

    # Create main window
    window = MainWindow(network, name)
    window.setWindowTitle(f"LAN 메신저 - {name}")
    window.show()

    # Connect to server
    def on_connect_failed(error_msg):
        QMessageBox.critical(window, "연결 실패", error_msg)

    network.connection_failed.connect(on_connect_failed)
    network.connect_to_server(server_ip, port, name)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
