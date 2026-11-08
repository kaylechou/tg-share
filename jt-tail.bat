@echo off
REM jt live-tail collector for Windows.
REM Double-click to run. It checks Node.js, installs wrangler,
REM logs in (browser opens - use jkaylechou@outlook.com, the B account),
REM then tails the jt Pages deployment and saves everything to
REM Desktop\jt-tail.txt. Press Ctrl+C after 2-3 minutes, then send
REM jt-tail.txt back to Muse for analysis.
REM Read-only: it only reads live logs, it changes nothing on Cloudflare.

echo === Step 1: check Node.js ===
node -v
if errorlevel 1 (
  echo Node.js is not installed. Install the LTS version from https://nodejs.org/ , reopen this file and run it again.
  pause
  exit /b 1
)

echo.
echo === Step 2: install / update wrangler ===
call npm install -g wrangler
if errorlevel 1 (
  echo npm install failed. Try running this file as administrator, then run it again.
  pause
  exit /b 1
)

echo.
echo === Step 3: wrangler login ===
echo A browser window will open. Log in with jkaylechou@outlook.com (the B account that owns jt).
call wrangler login

echo.
echo === Step 4: tail jt live logs ===
echo Tailing jt now. Internal errors happen about 18 times a minute, so 2-3 minutes is enough.
echo Output is being saved to %USERPROFILE%\Desktop\jt-tail.txt
echo Press Ctrl+C when 2-3 minutes have passed, then send jt-tail.txt back to Muse.
call wrangler pages deployment tail --project-name jt > "%USERPROFILE%\Desktop\jt-tail.txt" 2>&1

echo.
echo Done. The log is saved at %USERPROFILE%\Desktop\jt-tail.txt
echo Send that file back to Muse and it will find the internalError cause.
pause
