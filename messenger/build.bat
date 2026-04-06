@echo off
chcp 65001 >nul
echo ============================================
echo   LAN 메신저 - Windows 빌드 스크립트
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치해주세요.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/5] 의존성 설치 중...
pip install PyQt5>=5.15 pyinstaller>=6.0 --quiet
if errorlevel 1 (
    echo [오류] 패키지 설치 실패
    pause
    exit /b 1
)
echo       완료!
echo.

:: Generate icon if not exists
if not exist "installer\app_icon.ico" (
    echo [2/5] 아이콘 생성 중...
    python installer\create_icon.py
    echo       완료!
) else (
    echo [2/5] 아이콘 이미 존재함 - 건너뜀
)
echo.

:: Build client exe
echo [3/5] 클라이언트 빌드 중... (시간이 걸릴 수 있습니다)
pyinstaller installer\lan_messenger_client.spec --distpath dist --workpath build\client --clean --noconfirm
if errorlevel 1 (
    echo [오류] 클라이언트 빌드 실패
    pause
    exit /b 1
)
echo       완료!
echo.

:: Build server exe
echo [4/5] 서버 빌드 중...
pyinstaller installer\lan_messenger_server.spec --distpath dist --workpath build\server --clean --noconfirm
if errorlevel 1 (
    echo [오류] 서버 빌드 실패
    pause
    exit /b 1
)
echo       완료!
echo.

:: Check for Inno Setup
echo [5/5] 설치 파일 생성...
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined ISCC_PATH (
    "%ISCC_PATH%" installer\setup.iss
    if errorlevel 1 (
        echo [경고] 설치 파일 생성 실패
    ) else (
        echo       설치 파일 생성 완료!
    )
) else (
    echo [안내] Inno Setup이 설치되어 있지 않아 설치 파일을 생성할 수 없습니다.
    echo        Inno Setup 다운로드: https://jrsoftware.org/isdl.php
    echo.
    echo        Inno Setup 설치 후 다시 실행하거나,
    echo        dist 폴더의 exe 파일을 직접 배포할 수 있습니다.
)
echo.

echo ============================================
echo   빌드 완료!
echo ============================================
echo.
echo   생성된 파일:
echo     dist\LAN_Messenger.exe        (클라이언트)
echo     dist\LAN_Messenger_Server.exe (서버)
if exist "dist\installer\LAN_Messenger_Setup_v1.0.0.exe" (
    echo     dist\installer\LAN_Messenger_Setup_v1.0.0.exe (설치 파일)
)
echo.
echo   [사용법]
echo     1. LAN_Messenger.exe 실행
echo     2. "서버로 시작" 선택하면 서버+클라이언트 동시 실행
echo     3. 다른 PC에서는 "클라이언트로 접속" 선택 후 서버 IP 입력
echo.
pause
