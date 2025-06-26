@echo off
echo Starting Django project...
call venv\Scripts\activate
python manage.py runserver
pause

cd "C:\Users\app\Desktop\webapp_final77\webapplication"
git add .
git commit -m "Update project"
git push origin main
pause