"""
Конфигурация проекта.
Учётные данные можно переопределить через переменные окружения или файл .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://secby.ru")

# Обычный пользователь (роль: user)
USER_LOGIN    = os.getenv("USER_LOGIN",    "user")
USER_PASSWORD = os.getenv("USER_PASSWORD", "user")

# Администратор (роль: admin)
ADMIN_LOGIN    = os.getenv("ADMIN_LOGIN",    "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

TIMEOUT = 10
