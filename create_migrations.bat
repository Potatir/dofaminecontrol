@echo off
echo Creating Django migrations...
python manage.py makemigrations
echo Migrations created!
echo.
echo Applying migrations...
python manage.py migrate
echo Migrations applied successfully!
pause
