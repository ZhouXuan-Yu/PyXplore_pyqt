@echo off
REM PyXplore Desktop - Launch Script
REM Run with conda RAG environment

echo Starting PyXplore Desktop...
echo.

REM Activate RAG environment and run the application
call conda run -n RAG python "%~dp0main.py"

pause
