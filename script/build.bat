@echo off

for /F %%i in (.env.prod) do set %%i

taskkill /F /IM prospeed-v%1.exe 2>nul
if exist build\prospeed-v%1.exe del /F build\prospeed-v%1.exe

python -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-disable-console --include-package=socksio --include-package=speedtest --include-package=httpx --include-package=requests --output-dir=build --output-filename=prospeed-v%1.exe app/main.py
