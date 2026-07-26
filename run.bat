@echo off
echo Starting AI Meeting Summarizer...

if not exist .env (
    echo [ERROR] .env not found. Copy .env.example to .env and add your GROQ_API_KEY.
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "Meeting Backend" cmd /k "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Streamlit frontend on http://localhost:8501 ...
start "Meeting Frontend" cmd /k "streamlit run frontend/app.py --server.port 8501 --server.maxUploadSize 25"

echo.
echo Services started:
echo   Backend  : http://localhost:8000  (Swagger: http://localhost:8000/docs)
echo   Frontend : http://localhost:8501
echo.
pause
