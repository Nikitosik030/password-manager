# password-manager

Приложение для безопасного хранения паролей с шифрованием AES-128, генерацией и оценкой стойкости.

## Возможности

- **Хранение записей** — логин, пароль, URL, заметка в зашифрованном виде
- **Шифрование AES-128** — с деривацией ключа через PBKDF2 (100 000 итераций)
- **Генератор паролей** — настраиваемая длина и набор символов
- **Оценка стойкости** — по энтропии Шеннона (в битах)
- **Поиск записей** — по логину, URL и заметке
- **Экспорт хранилища** — в зашифрованном `.vault`-файле
- **GUI-интерфейс** — на базе встроенной библиотеки [Tkinter](https://docs.python.org/3/library/tkinter.html)
- **CLI-интерфейс** — на базе библиотеки [Click](https://click.palletsprojects.com/)
- **Docker-контейнеризация** — для запуска в изолированной среде

## Стек

| Технология | Назначение |
|---|---|
| Python 3.11+ | Основной язык |
| Tkinter | Графический интерфейс (GUI) |
| Click | Консольный интерфейс (CLI) |
| Cryptography | AES-128, PBKDF2 |
| Pytest | Тестирование |
| Docker | Контейнеризация |
| PyInstaller | Сборка EXE-файла |

## Структура проекта

```
.
├── data/
│ └── vault.vault # Зашифрованное хранилище
├── docs/
│ └── user_guide.md # Руководство пользователя
├── src/
│ ├── __init__.py
│ ├── cli.py # CLI-команды (Click)
│ ├── crypto.py # AES-128, PBKDF2
│ ├── gui.py # Графический интерфейс (Tkinter)
│ ├── main.py # Точка входа
│ ├── password_generator.py
│ ├── password_manager.py # Основная логика
│ ├── password_strength.py # Энтропия и оценка
│ └── storage.py # Работа с файлами
├── tests/
│ ├── test_crypto.py
│ ├── test_integration.py
│ ├── test_password_generator.py
│ └── test_password_strength.py
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Запуск

### Локально (GUI)

```bash
git clone https://github.com/Nikitosik030/password-manager.git
cd password-manager
pip install -r requirements.txt
python -m src.main
```
### Локально (CLI)

```bash
python -m src.main init
python -m src.main add --login test --generate
python -m src.main list
```
### Docker (CLI)

```bash
docker build -t password-manager .
docker run -it --rm -v $(pwd)/data:/app/data password-manager init
docker run -it --rm -v $(pwd)/data:/app/data password-manager add --login test --generate
docker run -it --rm -v $(pwd)/data:/app/data password-manager list
```
### EXE-файл (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name PasswordManager --add-data "src;src" src/main.py
# Готовый файл: dist/PasswordManager.exe
```
## Тестирование

```bash
pytest tests/ -v
```
## Алгоритмы

**AES-128 (GCM)**

```
E(data, key) = AES-128-GCM(data, key)
D(ciphertext, key) = AES-128-GCM_decrypt(ciphertext, key)
```

**PBKDF2**

```
key = PBKDF2(master_password, salt, iterations=100000, dklen=16)
```

**Энтропия Шеннона**

```
H = -∑ pᵢ · log₂(pᵢ)  (в битах на символ)
```
**Генератор паролей** — криптостойкий генератор на основе secrets.choice().


## Документация

- [`docs/user_guide.md`](docs/user_guide.md) — руководство пользователя

---

Учебно-ознакомительная практика, ВВГУ, кафедра ИТС, 2026.
Вариант Б-14 — Менеджер паролей.
