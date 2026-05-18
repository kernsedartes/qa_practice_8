# QA Practice 8 — API Autotests

Автотесты для Secure Authentication API (`https://secby.ru`).

## Что проверяется

- **Авторизация** — регистрация, логин, получение и отправка токена (`test_auth.py`)
- **Профиль пользователя** — получение информации о пользователе, ролевая модель (`test_user_profile.py`)
- **Администратор** — смена ролей, удаление профилей, смена пароля (`test_admin.py`)

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Создай файл `.env` в папке проекта:

```
BASE_URL=https://secby.ru
USER_LOGIN=your_user
USER_PASSWORD=your_password
ADMIN_LOGIN=your_admin
ADMIN_PASSWORD=your_admin_password
```

## Запуск

```bash
# Все тесты
pytest -v

# Один файл
pytest tests/test_auth.py -v
```
