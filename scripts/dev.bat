@echo off
setlocal

set "UV_CACHE_DIR=%CD%\.uv_cache"

uv venv --clear
uv sync
call .venv\Scripts\activate.bat

endlocal
