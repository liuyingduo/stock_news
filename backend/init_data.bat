@echo off
cd /d %~dp0
uv run python spider/init/init_events.py %*
pause
