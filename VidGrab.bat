@echo off
title VidGrab
cd /d "%~dp0"
where python >nul 2>nul && (set PY=python) || (set PY=py)
%PY% -c "import flask, yt_dlp" >nul 2>nul || %PY% -m pip install .
echo Starting VidGrab... keep this window open while you use it.
%PY% -m vidgrab web
pause
