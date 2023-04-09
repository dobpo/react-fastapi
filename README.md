# react-fastapi

В корне проекта:
- ```git submodule update --init```


**Backend**

Установка и запуск бэкенда (из папки backend):
- ```python3 -m venv venv && . ./venv/bin/activate && pip install -r requirements.txt```
- создать и заполнить конфиг ```db.env``` в ./backend по аналогии с ```db.env.example```
- ```sudo docker compose up -d```
- ```alembic revision --autogenerate -m "create users table"```
- ```alembic upgrade head```
- ```export PYTHONPATH=$(pwd)```
- ```python3 ./app/main.py```
- http://0.0.0.0:8000/api/docs

Доступ к БД:
- ```sudo docker exec -it postgres bash```
- ```psql "POSTGRES_DB_from_db.env" "POSTGRES_USER_from_db.env"```

**Frontend**

Установка и запуск фронтенда (из папки frontend):

- ```npm install```
- ```npm run start```
