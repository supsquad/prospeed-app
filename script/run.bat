@echo off

for /F %%i in (.env.%1) do set %%i

set PYTHONPATH=app

python app/main.py
