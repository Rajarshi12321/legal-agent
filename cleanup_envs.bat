@echo off
REM List all environments, filter out lines with "base" or "#"
for /f "tokens=1 delims= " %%i in ('conda env list ^| findstr /V "base" ^| findstr /V "#"') do (
    echo Removing environment: %%i
    conda env remove --name %%i --yes
)
pause
