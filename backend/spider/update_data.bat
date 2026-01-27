@echo off
cd /d D:\study\stock_news\backend
uv run python ../spider/update/update_events.py %*
pause
