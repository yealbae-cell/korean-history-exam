# LAN 메신저 (Local Network Messenger)

카카오톡 스타일의 로컬 네트워크 메신저입니다.

## 기능
- 카카오톡 스타일 UI (채팅 말풍선, 노란색 테마)
- 그룹 채팅방 생성 및 참여
- 파일 첨부 전송 (최대 50MB)
- 이름 기반 로그인 (최초 입력 후 자동 기억)
- LAN 내 자동 서버 탐색 (UDP 브로드캐스트)

## 설치

```bash
cd messenger
pip install -r requirements.txt
```

## 사용법

### 방법 1: 서버 + 클라이언트 통합 실행
클라이언트를 실행하면 로그인 화면에서 "서버로 시작"을 선택할 수 있습니다.

```bash
python run_client.py
```

1. 이름을 입력합니다
2. "서버로 시작"을 선택하면 서버가 내장되어 함께 실행됩니다
3. 다른 PC에서는 "클라이언트로 접속"을 선택하고 서버 IP를 입력합니다

### 방법 2: 서버 별도 실행
```bash
# 터미널 1: 서버 실행
python run_server.py

# 터미널 2+: 클라이언트 실행
python run_client.py
```

### 서버 옵션
```bash
python run_server.py --host 0.0.0.0 --port 9877
```

## 구조

```
messenger/
├── run_server.py          # 서버 실행 진입점
├── run_client.py          # 클라이언트 실행 진입점
├── requirements.txt       # 의존성 (PyQt5)
├── shared/
│   ├── constants.py       # 포트, 버퍼 크기 등 상수
│   └── protocol.py        # 통신 프로토콜 (JSON over TCP)
├── server/
│   └── server.py          # TCP 서버, 방 관리, 메시지 라우팅
└── client/
    ├── config.py           # 사용자 설정 저장/로드
    ├── network.py          # TCP 클라이언트 (PyQt 시그널 브릿지)
    └── ui/
        ├── main_window.py  # 메인 윈도우
        ├── login_dialog.py # 로그인 다이얼로그
        ├── chat_widget.py  # 채팅 영역
        ├── bubble_widget.py# 채팅 말풍선
        ├── sidebar_widget.py# 사이드바 (방 목록, 접속자)
        └── styles.py       # KakaoTalk 스타일 시트
```

## Windows 방화벽 설정
처음 실행 시 Windows 방화벽에서 Python 허용 여부를 묻는 팝업이 나올 수 있습니다.
"허용"을 선택해야 LAN 내 통신이 가능합니다.
