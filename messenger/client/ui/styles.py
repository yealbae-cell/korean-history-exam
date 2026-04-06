"""KakaoTalk-inspired stylesheet for LAN Messenger."""

MAIN_STYLE = """
QMainWindow {
    background-color: #FFFFFF;
}

/* Sidebar */
#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E5E5E5;
}

#sidebar_title {
    font-size: 18px;
    font-weight: bold;
    color: #1E1E1E;
    padding: 15px;
}

#room_list {
    background-color: #FFFFFF;
    border: none;
    font-size: 14px;
    outline: none;
}

#room_list::item {
    padding: 12px 15px;
    border-bottom: 1px solid #F5F5F5;
    color: #1E1E1E;
}

#room_list::item:selected {
    background-color: #F0F0F0;
    color: #1E1E1E;
}

#room_list::item:hover {
    background-color: #F8F8F8;
}

#user_list {
    background-color: #FFFFFF;
    border: none;
    font-size: 13px;
    outline: none;
}

#user_list::item {
    padding: 8px 15px;
    color: #555555;
}

/* Chat area */
#chat_header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E5E5;
    padding: 10px 15px;
    min-height: 30px;
}

#chat_header_label {
    font-size: 16px;
    font-weight: bold;
    color: #1E1E1E;
}

#chat_member_label {
    font-size: 12px;
    color: #999999;
}

#chat_area {
    background-color: #B2C7D9;
    border: none;
}

#message_input {
    border: 1px solid #E5E5E5;
    border-radius: 20px;
    padding: 8px 15px;
    font-size: 14px;
    background-color: #FFFFFF;
}

#message_input:focus {
    border-color: #FEE500;
}

#send_button {
    background-color: #FEE500;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: bold;
    color: #3C1E1E;
    min-width: 60px;
}

#send_button:hover {
    background-color: #FFD700;
}

#send_button:pressed {
    background-color: #E6CE00;
}

#attach_button {
    background-color: transparent;
    border: 1px solid #CCCCCC;
    border-radius: 20px;
    padding: 8px 12px;
    font-size: 16px;
    color: #666666;
}

#attach_button:hover {
    background-color: #F0F0F0;
}

/* Buttons */
#new_room_button {
    background-color: #FEE500;
    border: none;
    border-radius: 15px;
    padding: 8px 15px;
    font-size: 13px;
    font-weight: bold;
    color: #3C1E1E;
    margin: 5px 10px;
}

#new_room_button:hover {
    background-color: #FFD700;
}

#join_button {
    background-color: #FEE500;
    border: none;
    border-radius: 12px;
    padding: 5px 15px;
    font-size: 12px;
    font-weight: bold;
    color: #3C1E1E;
}

#leave_button {
    background-color: #FF6B6B;
    border: none;
    border-radius: 12px;
    padding: 5px 15px;
    font-size: 12px;
    font-weight: bold;
    color: #FFFFFF;
}

#section_label {
    font-size: 12px;
    font-weight: bold;
    color: #999999;
    padding: 10px 15px 5px 15px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
}

QScrollBar::handle:vertical {
    background: #CCCCCC;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
"""

# Colors for chat bubbles
MY_BUBBLE_COLOR = "#FEE500"        # KakaoTalk yellow
OTHER_BUBBLE_COLOR = "#FFFFFF"     # White
SYSTEM_COLOR = "#8FAABE"           # Muted blue-gray
CHAT_BG_COLOR = "#B2C7D9"         # KakaoTalk chat background
SENDER_NAME_COLOR = "#555555"
TIME_COLOR = "#7B8D97"
