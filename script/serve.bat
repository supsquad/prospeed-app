@echo off

for /F %%i in (.env.%1) do set %%i

python -m app.main