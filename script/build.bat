@echo off

for /F %%i in (.env.prod) do set %%i

python -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-disable-console --output-dir=build --output-filename=prospeed-v%1.exe app/main.py
