![workflow bagde](https://github.com/MorozovP/InstantShot/actions/workflows/main.yml/badge.svg)

### Общее описание

Проект Telegram бота, который по запросу пользователя присылает скриншот сайта.

### Технологии

Бот выполнен с помощью библиотеки python-telegram-bot. Взаимодействие с бд 
осуществляется посредством Django и Django REST API Framework. Подключена 
админка Django. Используемая база данных - Postgres, сервер - Nginx. Настроен
CI Github Actions с развертыванием проекта в четырех Docker - контейнерах: bot,
db-api, db, nginx.

### Установка
Клонируйте репозиторий
```
git clone git@github.com:MorozovP/InstantShot.git
```
Заполните файл с переменными окружения по шаблону: /.env.example 

Для запуска приложения в контейнерах перейдите в корневую директорию
проекта и выполните следующие команды:

- запустите контейнеры
```
docker compose up -d --build
```
- выполните миграции

```
docker compose exec db-api python manage.py migrate
```
- создайте администратора

```
docker compose exec db-api python manage.py createsuperuser
```
- для корректного отображения страниц выполните

```
docker compose exec db-api python manage.py collectstatic --no-input
```

