@echo off
set POSTGRES_DB=dofamine
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=123
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432

echo Starting Django server with PostgreSQL...
echo Database: %POSTGRES_DB%
echo User: %POSTGRES_USER%
echo Host: %POSTGRES_HOST%:%POSTGRES_PORT%

.venv\Scripts\python manage.py runserver


