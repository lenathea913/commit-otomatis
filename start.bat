@echo off
setlocal
cd /d "%~dp0"

rem --- Cek Python: coba "python" dulu, lalu launcher "py -3" ---
python --version >nul 2>nul
if not errorlevel 1 goto :jalankan_python

py -3 --version >nul 2>nul
if not errorlevel 1 goto :jalankan_py

echo.
echo ==================================================
echo  Python tidak ditemukan di komputer ini.
echo ==================================================
echo.
echo  Cara memperbaiki:
echo   1. Buka https://www.python.org/downloads/
echo   2. Unduh dan jalankan instalator Python
echo   3. PADA LAYAR PERTAMA, centang "Add python.exe to PATH"
echo   4. Tutup jendela ini, buka lagi, lalu jalankan start.bat
echo.
echo  Jika Python sudah terpasang tapi tetap gagal, cek di
echo  Command Prompt dengan perintah:  python --version
echo.
pause
exit /b 1

:jalankan_python
python "%~dp0main.py" %*
exit /b %errorlevel%

:jalankan_py
py -3 "%~dp0main.py" %*
exit /b %errorlevel%