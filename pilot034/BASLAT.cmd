@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
title SefaXTV 0.35 - Windows baslatici
cd /d "%~dp0.." || goto fail
set "ORIGINAL_PATH=%PATH%"
set "PYTHONNOUSERSITE=1"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"
set "CHECK_ONLY="
if /i "%~1"=="--check-only" set "CHECK_ONLY=1"
if not defined CHECK_ONLY if not exist "pilot034\hls.mjs" (echo Paket eksik. BASLAT.cmd dosyasini pilot034 klasorune koyun. & goto fail)
if not exist "pilot030\requirements.txt" (echo Paket eksik: pilot030\requirements.txt & goto fail)
if not exist "pilot034\local.py" (echo Paket eksik: pilot034\local.py & goto fail)
echo [1/4] Python 3.11 x64 kontrolu...
call :findpython
if defined PYEXE goto python_ok
if defined CHECK_ONLY goto fail
call :winget_check || goto fail
echo Python 3.11 eksik. WinGet ile kullanici hesabina kuruluyor...
winget install --id Python.Python.3.11 --exact --source winget --scope user --architecture x64 --silent --accept-package-agreements --accept-source-agreements
call :refreshpath
call :findpython
if not defined PYEXE (echo Python 3.11 kurulumu tamamlanamadi. & goto fail)
:python_ok
echo Python: "%PYEXE%"
echo [2/4] FFmpeg ve ffprobe kontrolu...
call :refreshpath
call :checkffmpeg
if not errorlevel 1 goto ffmpeg_ok
if defined CHECK_ONLY goto fail
call :winget_check || goto fail
echo FFmpeg eksik. WinGet ile kullanici hesabina kuruluyor...
winget install --id Gyan.FFmpeg --exact --source winget --scope user --architecture x64 --silent --accept-package-agreements --accept-source-agreements
call :refreshpath
call :checkffmpeg
if errorlevel 1 (echo FFmpeg kurulumu tamamlanamadi veya gerekli kodlayici yok. & goto fail)
:ffmpeg_ok
if defined CHECK_ONLY (echo PASS Python 3.11 x64 and FFmpeg readiness & exit /b 0)
echo [3/4] Yerel dublaj kutuphaneleri kontrol ediliyor...
set "VPY=%CD%\.venv311\Scripts\python.exe"
if not exist "%VPY%" (
  "%PYEXE%" -m venv ".venv311" || goto fail
)
"%VPY%" -c "import sys; assert sys.version_info[:2]==(3,11) and sys.maxsize>2**32" || goto fail
call :checklibs
if not errorlevel 1 goto libs_ok
echo Eksik kutuphaneler indiriliyor. Ilk calistirma buyuk indirme gerektirebilir.
"%VPY%" -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 || goto fail
"%VPY%" -m pip install -r "pilot030\requirements.txt" || goto fail
call :checklibs
if errorlevel 1 (echo Kutuphane kontrolu basarisiz. Yukaridaki hata mesajini kaydedin. & goto fail)
:libs_ok
echo [4/4] SefaXTV baslatiliyor. Modeller ilk seferde indirilebilir.
echo Tarayici otomatik acilacak. index.html dosyasini elle acmayin.
"%VPY%" "pilot034\local.py"
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" goto fail
echo Oturum sonlandi.
pause
exit /b 0
:findpython
set "PYEXE="
call :trypython "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if defined PYEXE exit /b 0
call :trypython "%ProgramFiles%\Python311\python.exe"
if defined PYEXE exit /b 0
where py.exe >nul 2>&1
if not errorlevel 1 for /f "delims=" %%I in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do call :trypython "%%I"
if defined PYEXE exit /b 0
for /f "delims=" %%I in ('where python.exe 2^>nul ^| findstr /i /v /c:"\WindowsApps\"') do call :trypython "%%I"
exit /b 0
:trypython
if defined PYEXE exit /b 0
if not exist "%~1" exit /b 0
"%~1" -c "import sys; assert sys.version_info[:2]==(3,11) and sys.maxsize>2**32" >nul 2>&1
if not errorlevel 1 set "PYEXE=%~1"
exit /b 0
:refreshpath
for /f "delims=" %%P in ('powershell.exe -NoProfile -NonInteractive -Command "[Environment]::ExpandEnvironmentVariables([Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User'))"') do set "PATH=%%P;%ORIGINAL_PATH%"
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%ProgramFiles%\WinGet\Links;%PATH%"
exit /b 0
:winget_check
where winget.exe >nul 2>&1
if errorlevel 1 (echo WinGet bulunamadi. Microsoft Store'dan App Installer guncellenmeli. & exit /b 1)
exit /b 0
:checkffmpeg
ffmpeg -version >nul 2>&1 || exit /b 1
ffprobe -version >nul 2>&1 || exit /b 1
ffmpeg -hide_banner -encoders 2>nul | findstr /c:"libx264" >nul || exit /b 1
exit /b 0
:checklibs
"%VPY%" -m pip check || exit /b 1
"%VPY%" -c "import importlib.metadata as m; from pathlib import Path; from packaging.requirements import Requirement; import torch, faster_whisper, transformers, sentencepiece, sacremoses, piper; assert torch.__version__.split('+')[0]=='2.6.0'; assert all(Requirement(s).specifier.contains(m.version(Requirement(s).name)) for s in Path('pilot030/requirements.txt').read_text().splitlines() if s.strip())" || exit /b 1
exit /b 0
:fail
echo.
echo BASLATILAMADI. Yukaridaki hata mesajini ekran goruntusu ile gonderin.
if not defined CHECK_ONLY pause
exit /b 1
