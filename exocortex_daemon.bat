@echo off
title EXOCORTEX SOCIAL DAEMON
color 0A

echo [*] EXOCORTEX DAEMON STARTED
echo [*] The Ghost is in the Shell.
echo [*] Interval: 20 Minutes (Accelerated Learning).

:loop
echo.
echo [DATE %date% TIME %time%] Waking up...
python synapse.py --social
echo [Zzz] Sleeping for 20 minutes...
timeout /t 1200 >nul
goto loop
