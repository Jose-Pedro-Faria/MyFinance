@echo off
cd /d "%~dp0"
docker compose exec -T web python manage.py backup