@echo off
echo.
echo Water Reminder - starting...
echo Icon in system tray (taskbar right corner)
echo.
pause >nul
start "" pythonw "%~dp0water_reminder.py"
exit
