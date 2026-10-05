@echo off
setlocal enabledelayedexpansion

rem If HYTALE_SERVER_JAR is not provided, try Hytale's documented Windows install path.
if "%HYTALE_SERVER_JAR%"=="" (
  set "HYTALE_SERVER_JAR=%APPDATA%\Hytale\install\release\package\game\latest\Server\HytaleServer.jar"
  echo HYTALE_SERVER_JAR not set; trying default Hytale install path:
  echo   !HYTALE_SERVER_JAR!
)

if not exist "%HYTALE_SERVER_JAR%" (
  echo ERROR: HytaleServer.jar was not found at:
  echo   %HYTALE_SERVER_JAR%
  echo.
  echo Set it manually, for example:
  echo   set HYTALE_SERVER_JAR=C:\full\path\to\HytaleServer.jar
  exit /b 1
)

java -version 2>&1 | findstr /r "25\." >nul
if errorlevel 1 (
  echo ERROR: Hytale's official server manual currently requires Java 25.
  echo Install/select Java 25, then run this script again.
  java -version
  exit /b 1
)

if exist build rmdir /s /q build
mkdir build\classes

dir /s /b src\main\java\*.java > build\sources.txt
javac --release 25 -cp "%HYTALE_SERVER_JAR%" -d build\classes @build\sources.txt
if errorlevel 1 exit /b 1

copy /y src\main\resources\manifest.json build\classes\manifest.json >nul
jar --create --file build\HytaleAnalyticsCollector-0.2.0.jar -C build\classes .
if errorlevel 1 exit /b 1

echo.
echo Built: build\HytaleAnalyticsCollector-0.2.0.jar
echo Hytale API used: %HYTALE_SERVER_JAR%
endlocal
