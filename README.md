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
# Заполни .env реальными логинами
```

## Запуск

```bash
# Все тесты
pytest -v

# С HTML-отчётом
pytest -v --html=report.html --self-contained-html

# Только одна папка
pytest tests/auth/ -v
```

## Структура проекта

```
qa_practice_8/
├── config.py                        # BASE_URL и учётные данные
├── conftest.py                      # Общие фикстуры
├── utils/
│   └── api_client.py                # Клиент API
├── tests/
│   ├── auth/
│   │   ├── test_register.py         # POST /api/auth/register
│   │   ├── test_login.py            # POST /api/auth/login
│   │   └── test_verify.py           # POST /api/auth/verify
│   ├── profiles/
│   │   ├── test_my_profile.py       # GET /api/profiles/me
│   │   ├── test_list_profiles.py    # GET /api/profiles/
│   │   └── test_access_control.py  # GET /api/profiles/{id}
│   └── admin/
│       ├── test_change_role.py      # PUT /api/profiles/{id}/role
│       ├── test_change_password.py  # POST /api/auth/change-password
│       └── test_delete_profile.py  # DELETE /api/profiles/{id}
├── .env.example
├── requirements.txt
└── README.md
```

