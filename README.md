[![Main Foodgram workflow](https://github.com/wArahh/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/wArahh/kittygram_final/actions/workflows/main.yml)

my_syte = https://warahsfoodgram.ddns.net/

# Foodgram
Данный проект создан для создания и публикаций рецептов.

## Стек
- DRF
- Nginx
- Docker
- Gunicorn

## Шаги по развертыванию проекта "Foodgram":

1. **Скачайте необходимые файлы:**
   - Скачайте файл `docker-compose.yml`.
   - Создайте файл `.env` для хранения переменных окружения.

2. **Заполните файл `.env` согласно вашей конфигурации и требованиям проекта:**
   ```plaintext
   POSTGRES_USER=<ваше_имя_пользователя>
   POSTGRES_PASSWORD=<ваш_пароль>
   POSTGRES_DB=<название_базы_данных>
   DB_HOST=<хост_базы_данных>
   DB_PORT=<порт_базы_данных>
   ALLOWED_HOSTS=<список_разрешенных_хостов>
   DEBUG=<True/False>
   DATABASES=<POSTGRES/SQLITE>
   ```

3. **Создайте файл с переменными окружения (необходимые переменные в `.env`):**
   - Указанные переменные должны соответствовать вашей среде и требованиям проекта.

4. **Развертывание проекта:**
   - Запустите Docker Compose с помощью `docker-compose up -d` для развертывания контейнеров с проектом.
   - Проверьте работоспособность приложения, обращаясь к соответствующему хосту и порту.


