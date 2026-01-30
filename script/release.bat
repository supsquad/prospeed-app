@echo off

for /F %%i in (.env.prod) do set %%i

git tag v%1
git push origin v%1
gh release create v%1 ./build/prospeed-v%1.exe#prospeed-v%1.exe --title "v%1" --notes-file=./README.md --latest
