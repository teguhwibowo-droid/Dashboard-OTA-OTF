@echo off
REM ============================================================
REM  setup_github.bat
REM  Jalankan sekali untuk init git repo & push ke GitHub
REM ============================================================

echo.
echo =============================================
echo   SETUP GIT REPO - Dashboard OTA
echo =============================================
echo.

REM Minta URL repo GitHub dari user
set /p REPO_URL="Masukkan URL repo GitHub (contoh: https://github.com/username/dashboard-ota.git): "

REM Init git kalau belum
if not exist ".git" (
    echo [1/5] Inisialisasi git repo...
    git init
    git branch -M main
) else (
    echo [1/5] Repo git sudah ada, skip init.
)

REM Tambah .gitignore
echo [2/5] Membuat .gitignore...
(
echo service_account.json
echo __pycache__/
echo *.pyc
echo .env
) > .gitignore

REM Add semua file
echo [3/5] Menambahkan semua file...
git add .
git commit -m "🚀 Initial commit: Dashboard OTA + GitHub Actions"

REM Set remote
echo [4/5] Menghubungkan ke GitHub...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

REM Push
echo [5/5] Push ke GitHub...
git push -u origin main

echo.
echo =============================================
echo   DONE! Sekarang buka GitHub dan:
echo   1. Pergi ke Settings -> Pages
echo      Set Source: "GitHub Actions"
echo   2. Pergi ke Settings -> Secrets and variables -> Actions
echo      Tambahkan 3 secrets:
echo        SPREADSHEET_ID
echo        SHEET_NAME
echo        GOOGLE_SERVICE_ACCOUNT_JSON
echo =============================================
echo.
pause
