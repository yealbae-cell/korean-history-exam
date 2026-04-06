@echo off
chcp 65001 >nul
echo ============================================
echo   LAN 메신저 - 포터블 빌드 (Inno Setup 불필요)
echo ============================================
echo.
echo   이 스크립트는 exe 파일만 생성합니다.
echo   설치 파일 없이 exe를 직접 배포할 수 있습니다.
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/4] 의존성 설치 중...
pip install PyQt5>=5.15 pyinstaller>=6.0 --quiet
echo       완료!
echo.

:: Generate icon
if not exist "installer\app_icon.ico" (
    echo [2/4] 아이콘 생성 중...
    python installer\create_icon.py
) else (
    echo [2/4] 아이콘 확인 완료
)
echo.

:: Build client
echo [3/4] 클라이언트 빌드 중...
pyinstaller installer\lan_messenger_client.spec --distpath dist --workpath build\client --clean --noconfirm
echo       완료!
echo.

:: Build server
echo [4/4] 서버 빌드 중...
pyinstaller installer\lan_messenger_server.spec --distpath dist --workpath build\server --clean --noconfirm
echo       완료!
echo.

echo ============================================
echo   빌드 완료!
echo ============================================
echo.
echo   dist\LAN_Messenger.exe        (클라이언트 - 이것만 배포하면 됩니다)
echo   dist\LAN_Messenger_Server.exe (서버 전용 - 선택사항)
echo.
echo   LAN_Messenger.exe 하나로 서버+클라이언트 모두 가능합니다!
echo.
pause
