@echo off
echo Starting Django project...
call venv\Scripts\activate
python manage.py runserver
pause 