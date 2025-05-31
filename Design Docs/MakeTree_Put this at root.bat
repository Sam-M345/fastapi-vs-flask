@echo off
cd /d "%~dp0"

::--------------------------------------------------------------
:: Create File_Tree.txt
::   • First line is blank
::   • Second line shows date stamp
::   • Third line shows the exact root path
::   • Fourth line is blank for readability
::   • Remaining tree (skips the header 3 lines from TREE output)
::--------------------------------------------------------------
> "File_Tree.txt" (
    echo.
    echo File Tree as of %date%
    echo Root Path: %CD%
    echo.
    for /f "skip=3 delims=" %%L in ('tree /f /a') do echo(  %%L
)
