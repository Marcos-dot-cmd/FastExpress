@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe -m pytest --cov=backend --cov-branch --cov-report=term-missing --cov-report=html:evidencias/htmlcov --cov-report=json:evidencias/coverage.json --junitxml=evidencias/junit.xml > evidencias\resultado_pruebas.txt 2>&1
set TEST_RESULT=%ERRORLEVEL%
type evidencias\resultado_pruebas.txt
if not "%TEST_RESULT%"=="0" exit /b %TEST_RESULT%
.venv\Scripts\python.exe scripts\check_coverage.py
