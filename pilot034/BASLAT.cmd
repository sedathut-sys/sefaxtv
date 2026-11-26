@echo off
cd /d "%~dp0.."
where py >nul 2>&1 || (echo Python 3.11 kurulu olmali. & pause & exit /b 1)
where ffmpeg >nul 2>&1 || (echo FFmpeg PATH uzerinde olmali. & pause & exit /b 1)
where ffprobe >nul 2>&1 || (echo ffprobe PATH uzerinde olmali. & pause & exit /b 1)
if not exist ".venv\Scripts\python.exe" py -3.11 -m venv .venv || (pause & exit /b 1)
if not exist ".venv\sefa-ready" (
 ".venv\Scripts\python.exe" -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 || (pause & exit /b 1)
 ".venv\Scripts\python.exe" -m pip install -r pilot030\requirements.txt || (pause & exit /b 1)
 echo ready> ".venv\sefa-ready"
)
".venv\Scripts\python.exe" pilot034\local.py
pause
