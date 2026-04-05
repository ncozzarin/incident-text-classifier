@echo off
REM Security Incident Classification System - Windows Startup Script
REM This script initializes and starts the development environment

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and fill in your environment variables.
    copy .env.example .env
    echo Edit .env file with your configuration and run this script again.
    pause
    exit /b
)

REM Create necessary directories
if not exist backend\uploads mkdir backend\uploads
if not exist logs mkdir logs

REM Start all services
echo Starting Security Incident Classification System...
echo =========================================
echo SERVICES:
echo - PostgreSQL DB (port 5432)
echo - Redis (port 6379)
echo - FastAPI Backend (port 8000)
echo - React Frontend (port 3000)
echo =========================================

docker-compose up --build

pause
