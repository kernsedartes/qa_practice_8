# QA Practice 8 — API Autotests

Набор автотестов для **Secure Authentication API**: https://secby.ru

## Стек
- Python 3.10+
- pytest + pytest-html
- requests
- python-dotenv

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

```bash
cp .env.example .env
# Отредактируй .env — укажи реальные логины/пароли
```

## Запуск

```bash
# Все тесты с подробным выводом
pytest -v

# С HTML-отчётом
pytest -v --html=report.html --self-contained-html

# Один файл
pytest tests/test_auth.py -v
```

## Структура проекта

```
qa_practice_8/
├── config.py                    # BASE_URL и учётные данные
├── conftest.py                  # Общие фикстуры (токены, регистрация)
├── utils/
│   └── api_client.py            # Клиент API (все эндпоинты)
├── tests/
│   ├── test_auth.py             # Регистрация, логин, верификация токена
│   ├── test_user_profile.py     # Профиль пользователя, ролевая модель
│   └── test_admin.py            # Смена роли, удаление, смена пароля
├── .env.example
├── requirements.txt
└── README.md
```

## Покрытие по требованиям задания

| Требование | Файл | Тесты |
|---|---|---|
| Проверка авторизации (логин, токен, отправка токена) | `test_auth.py` | `TestLogin`, `TestVerifyToken` |
| Получение информации о пользователе (User Profile) | `test_user_profile.py` | `TestGetMyProfile`, `TestListProfiles` |
| Получение информации об администраторе | `test_admin.py`, `test_user_profile.py` | `TestChangeRole`, `TestProfileAccessControl` |

## Реальные эндпоинты API

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Логин → JWT |
| POST | `/api/auth/verify` | Верификация токена |
| POST | `/api/auth/change-password` | Смена пароля |
| GET | `/api/profiles/me` | Свой профиль |
| GET | `/api/profiles/` | Список профилей |
| GET | `/api/profiles/{id}` | Профиль по ID |
| PUT | `/api/profiles/{id}/role` | Смена роли (admin only) |
| DELETE | `/api/profiles/{id}` | Удаление (admin only) |
