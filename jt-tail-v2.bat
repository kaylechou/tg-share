@echo off
REM jt live-tail collector for Windows - v2.
REM Double-click to run. It checks Node.js, installs wrangler,
REM logs in (browser opens - use jkaylechou@outlook.com, the B account),
REM then tails the jt Pages deployment and saves everything to
REM Desktop\jt-tail.txt. Press Ctrl+C after 2-3 minutes, then send
REM jt-tail.txt back to Muse for analysis.
REM Read-only: it only reads live logs, it changes nothing on Cloudflare.
REM
REM v2 fix (2026-11-08): wrangler 4.158.0 refuses
REM   wrangler pages deployment tail --project-name jt
REM in non-interactive mode ("Missing deployment. In non-interactive
REM mode, provide the deployment ID or URL as a positional argument").
REM So Step 4 now passes jt's current production deployment ID
REM (105edc50-5533-44fc-8334-79b364c5d952, deployed 2026-10-11).
REM If jt is redeployed later, this ID changes: tell Muse and the
REM bat will be updated with the new deployment ID.

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
call wrangler pages deployment tail 105edc50-5533-44fc-8334-79b364c5d952 --project-name jt > "%USERPROFILE%\Desktop\jt-tail.txt" 2>&1

echo.
echo Done. The log is saved at %USERPROFILE%\Desktop\jt-tail.txt
echo Send that file back to Muse and it will find the internalError cause.
pause
