@echo off
echo ================================
echo AI Meeting Assistant Startup
echo ================================
echo.

echo Starting Backend Server...
start /B "Backend Server" cmd /c "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start /B "Frontend Server" cmd /c "cd frontend && npm start"

echo.
echo ================================
echo Application is starting up!
echo ================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause > nul

echo Stopping servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
echo Done.
