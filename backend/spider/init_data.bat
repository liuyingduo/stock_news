@echo off
cd /d D:\study\stock_news\backend
uv run python ../spider/init/init_events.py %*
pause
