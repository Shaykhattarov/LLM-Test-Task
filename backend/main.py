import os
import logging

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.routers import global_router



# Инициализация проекта
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    # lifespan=lifespan,
)

# Настройка логирования
log_filename = os.path.join(
    os.path.dirname(__file__), 
    "logs", 
    f"backend-{datetime.now().strftime('%Y-%m-%d')}.logs"
)

logging.basicConfig(
    level=logging.INFO,
    filename=log_filename,
    filemode="a"
)


# Включение настроек CORS
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Добавление роутеров
app.include_router(global_router, prefix=settings.API_STR)

