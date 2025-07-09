## Загрузка проекта локально
    Выполнить команду:
```bash
    git clone https://github.com/Shaykhattarov/LLM-Test-Task.git
```

## Используемое окружение
    - ОС Windows
    - Visual Studio Code
    - Python 3.13
    - Uv (Виртуальное окружение Python)
    - Docker Desktop
    - WSL2
    
### Настройка окружения
    Для запуска проекта необходимо создать .env файл (Пример .env файла отображен в файле .env-example).
    И заполнить следующие строки своими данными:
    ```text
        # Project Settings
        PROJECT_NAME="<Your project name>"
        DEBUG="<True | False>"
        
        # Postgre environment values
        POSTGRES_DB="<postgres_database_name>"
        POSTGRES_HOST="<postgres_container"
        POSTGRES_USER="<postgre_username>"
        POSTGRES_PASSWORD="<postgre_password>"

        # PGAdmin Settings
        PGADMIN_DEFAULT_EMAIL="<pgadmin_email>"
        PGADMIN_DEFAULT_PASSWORD="<pgadmin_password>"

        # Telegram token
        TELEGRAM_TOKEN="<Your telegram token>"
    ```

#### Дополнительно:
    - Установить "nvidia-container-toolkit" для запуска LLM на GPU

## Запуск проекта

    Первый запуск проекта:
    ```bash
        cd ./LLM-Test-Task/
        docker-compose build
        docker-compose up -d
    ```

    После запуска проекта необходимо выполнить (Для использования другой модели изменить llama3.2 на другое наименование):
    ```bash
        docker exec -t ibs-ollama-1 ollama pull llama3.2
    ```

    Остановка проекта:
    ```bash
        docker-compose down
    ```

## Список доступных сервисов для работы с проектом

    - Сервис Web-интерфейса: http://localhost:8000/
    - Сервис PostgreSQL Admin: http://localhost:8081/
    - Сервис RabbitMQ: http://localhost:15672/
