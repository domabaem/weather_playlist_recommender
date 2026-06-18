@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI Lecture Notes

echo ============================================
echo    AI Lecture Notes  -  실행
echo ============================================
echo.

REM --- 파이썬 실행기 탐지 (python 우선, 없으면 py) ---
set "PY=python"
%PY% --version >nul 2>&1
if errorlevel 1 set "PY=py"
%PY% --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python 을 찾을 수 없습니다.
    echo        https://www.python.org 에서 설치 후, 설치 중 "Add Python to PATH" 체크하세요.
    echo.
    pause
    exit /b
)

REM --- 필요한 패키지가 없으면 설치 ---
%PY% -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo [설치] 필요한 패키지를 설치합니다. 처음 한 번만 시간이 걸립니다...
    %PY% -m pip install -r requirements.txt
    echo.
)

REM --- API 키 준비 (환경변수 > apikey.txt > 직접 입력) ---
if "%ANTHROPIC_API_KEY%"=="" if exist apikey.txt set /p ANTHROPIC_API_KEY=<apikey.txt
if "%ANTHROPIC_API_KEY%"=="" (
    echo ANTHROPIC API 키가 필요합니다. ^(sk-ant- 로 시작^)
    set /p ANTHROPIC_API_KEY=키를 붙여넣고 Enter: 
    echo.
    echo [팁] 매번 입력하기 싫으면, 이 폴더에 apikey.txt 를 만들고 키 한 줄만 넣어두세요.
    echo.
)

REM --- 실행 ---
echo 브라우저가 자동으로 열립니다.  종료하려면 이 검은 창에서 Ctrl+C.
echo.
%PY% -m streamlit run app.py

echo.
echo (앱이 종료되었습니다.)
pause
