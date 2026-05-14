@echo off
chcp 65001 >nul
cd /d "%~dp0"

:MENU
cls
echo.
echo   ╔═══════════════════════════╗
echo   ║      音 伴 — 选 单        ║
echo   ╚═══════════════════════════╝
echo.
echo   1. 和 AI 聊天
echo   2. 每日推荐
echo   3. 按心情推荐
echo   4. 按场景推荐
echo   5. 发现新歌手
echo   6. 语音播客
echo   7. 听歌报告
echo   8. 查看配置
echo   9. Web 界面（需安装 gradio）
echo   0. 退出
echo.
set /p choice="请选择 (0-9): "

if "%choice%"=="1" goto CHAT
if "%choice%"=="2" goto DAILY
if "%choice%"=="3" goto MOOD
if "%choice%"=="4" goto SCENE
if "%choice%"=="5" goto DISCOVER
if "%choice%"=="6" goto PODCAST
if "%choice%"=="7" goto REPORT
if "%choice%"=="8" goto CONFIG
if "%choice%"=="9" goto WEB
if "%choice%"=="0" exit /b

echo 无效输入，请重新选择
timeout /t 2 >nul
goto MENU

:CHAT
cls
echo 正在启动聊天...
python main.py chat
echo.
pause
goto MENU

:DAILY
cls
python main.py daily
echo.
pause
goto MENU

:MOOD
cls
echo 可选心情：开心、平静、伤感、烦躁、慵懒、热情
set /p mood="输入心情: "
python main.py recommend --mood "%mood%"
echo.
pause
goto MENU

:SCENE
cls
echo 可选场景：深夜、学习、跑步、通勤、工作
set /p scene="输入场景: "
python main.py recommend --scene "%scene%"
echo.
pause
goto MENU

:DISCOVER
cls
python main.py discover
echo.
pause
goto MENU

:PODCAST
cls
python main.py podcast --no-tts
echo.
pause
goto MENU

:REPORT
cls
python main.py report
echo.
pause
goto MENU

:CONFIG
cls
python main.py config list
echo.
pause
goto MENU

:WEB
cls
python main.py web
echo.
pause
goto MENU
