@echo off
cd /d %~dp0
uv run python spider/update/update_events.py %*
pause
