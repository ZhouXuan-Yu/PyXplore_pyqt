@echo off
chcp 65001 >nul

REM ============================================================
REM 打包必须使用 Python 3.10.x（推荐 3.10.18）
REM 若 PATH 里默认是 3.14，请设置下面路径或环境变量 PYTHON310_EXE
REM ============================================================
if not defined PYTHON310_EXE (
    set "PYTHON310_EXE=D:\StabilityMatrix-win-x64\Data\Assets\Python\cpython-3.10.18-windows-x86_64-none\python.exe"
)

echo ============================================================
echo   PyXplore Desktop - Build Script
echo ============================================================
echo.

if not exist "%PYTHON310_EXE%" (
    echo [ERROR] 未找到 Python 3.10.18 解释器:
    echo        %PYTHON310_EXE%
    echo.
    echo 请安装 CPython 3.10.18，或在运行本脚本前设置:
    echo   set PYTHON310_EXE=你的路径\python.exe
    echo.
    pause
    exit /b 1
)

echo [INFO] Using Python: %PYTHON310_EXE%
for /f "delims=" %%v in ('"%PYTHON310_EXE%" --version 2^>^&1') do echo        %%v

"%PYTHON310_EXE%" -c "import sys; exit(0 if sys.version_info[:2]==(3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 当前解释器不是 Python 3.10.x，不能用于本脚本约定的打包环境。
    "%PYTHON310_EXE%" --version
    pause
    exit /b 1
)

set "BDIR=%~dp0"
set "BDIR=%BDIR:~0,-1%"

for %%i in ("%BDIR%") do set "BDIR=%%~fi"

echo [INFO] Script directory: %BDIR%

set "CAND=%BDIR%"
:search_loop
if exist "%CAND%\PyXplore_Desktop.spec" (
    set "PROOT=%CAND%"
    goto :root_ok
)
for %%i in ("%CAND%") do set "CAND=%%~dpi.."
for %%i in ("%CAND%") do set "CAND=%%~fi"
if not "%CAND%"=="%PROOT_PREV%" (
    set "PROOT_PREV=%CAND%"
    goto :search_loop
)
set "PROOT=%BDIR%"

:root_ok
echo [INFO] Project root: %PROOT%

cd /d "%PROOT%"

if not exist "PyXplore_Desktop.spec" (
    echo.
    echo [ERROR] PyXplore_Desktop.spec not found!
    pause
    exit /b 1
)

echo.
echo [1/4] Python OK (3.10.x for packaging)

echo.
echo [2/4] Checking PyInstaller...
"%PYTHON310_EXE%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller into this Python...
    "%PYTHON310_EXE%" -m pip install pyinstaller
)
for /f "delims=" %%v in ('"%PYTHON310_EXE%" -m PyInstaller --version 2^>^&1') do echo        %%v

echo.
echo [3/4] Checking dependencies...
"%PYTHON310_EXE%" -c "import PyQt5, numpy, scipy, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    "%PYTHON310_EXE%" -m pip install PyQt5 numpy scipy matplotlib pandas sympy scikit-learn PyWavelets tqdm plotly monty pymatgen ase
) else (
    echo Dependencies OK
)

echo.
echo [4/4] Cleaning old build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo [Building] with Python 3.10.x ...
"%PYTHON310_EXE%" -m PyInstaller PyXplore_Desktop.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] Build complete!
echo ============================================================
echo.
echo Run: %PROOT%\dist\PyXplore_Desktop\PyXplore_Desktop.exe
echo.
echo PyInstaller 日志中应显示: Python: 3.10.x （不是 3.14）
echo.
pause
