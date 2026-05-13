# Project Structure

Проект организован в модульную структуру для лучшей управляемости и масштабируемости.

```
proxmox-metrics/
├── 📁 src/                          # Исходный код Python
│   ├── __init__.py                  # Package инициализация
│   ├── main.py                      # Главный модуль с ProxmoxMonitor
│   ├── proxmox.py                   # Сбор метрик Proxmox
│   ├── alerts.py                    # Логика алертов
│   └── telegram.py                  # Telegram бот
│
├── 📁 docs/                         # Документация (все .md файлы)
│   ├── README.md                    # Полное руководство
│   ├── INDEX.md                     # Навигация по документам
│   ├── QUICKSTART.md                # Быстрый старт (5 минут)
│   ├── CONFIG_REFERENCE.md          # Справка по конфигурации
│   ├── DEPLOYMENT.md                # Развёртывание
│   ├── PROJECT_SUMMARY.md           # Описание проекта
│   └── COMPLETION_SUMMARY.md        # Статус завершения
│
├── 📁 config/                       # Конфигурационные файлы
│   └── config.yaml                  # Основная конфигурация (кастомизировать)
│
├── 📁 scripts/                      # Утилиты и скрипты
│   ├── install.sh                   # Автоматическая установка
│   ├── health_check.py              # Проверка перед деплойментом
│   └── verify_syntax.py             # Проверка синтаксиса Python
│
├── 📁 systemd/                      # Systemd unit файлы
│   ├── proxmox-monitor.service      # Service unit (основной сервис)
│   └── proxmox-monitor.timer        # Timer unit (планировщик)
│
├── 📄 main.py                       # Точка входа (wrapper для src/main.py)
├── 📄 pyproject.toml                # Конфигурация проекта и зависимости
├── 📄 .gitignore                    # Git exclude patterns
└── 📁 state.json                    # Состояние алертов (auto-generated)
```

## Назначение каждой папки

### 📁 `src/` - Исходный код
Содержит все Python модули приложения:
- **main.py** - Основной класс `ProxmoxMonitor`, запуск приложения
- **proxmox.py** - Сбор метрик (CPU, RAM, Disk, Containers, VMs)
- **alerts.py** - Логика алертов с дедупликацией
- **telegram.py** - Telegram бот и форматирование сообщений

**Импорты:**
```python
from src.proxmox import ProxmoxCollector
from src.alerts import AlertGenerator
from src.telegram import TelegramBot
```

### 📁 `docs/` - Документация
Все markdown файлы с документацией:
- **README.md** - Полное руководство (800+ строк)
- **QUICKSTART.md** - Быстрый старт за 5 минут
- **CONFIG_REFERENCE.md** - Все параметры конфигурации
- **DEPLOYMENT.md** - Пошаговое развёртывание в production
- **PROJECT_SUMMARY.md** - Архитектура и компоненты
- **INDEX.md** - Навигация по всей документации

**Используется для:** чтения, обучения, поиска информации

### 📁 `config/` - Конфигурация
- **config.yaml** - Основной файл конфигурации
  - Telegram параметры
  - Proxmox настройки
  - Пороги алертов
  - Расписание задач

**Важно:** Кастомизировать этот файл перед запуском!

### 📁 `scripts/` - Утилиты
- **install.sh** - Автоматическая установка всего проекта
- **health_check.py** - Проверка перед деплойментом
- **verify_syntax.py** - Проверка синтаксиса Python кода

**Команды:**
```bash
sudo bash scripts/install.sh
python3 scripts/health_check.py
python3 scripts/verify_syntax.py
```

### 📁 `systemd/` - Systemd Units
- **proxmox-monitor.service** - Service unit (автозапуск)
- **proxmox-monitor.timer** - Timer unit (периодический запуск)

**Используется для:**
- `systemctl start proxmox-monitor.service`
- `systemctl status proxmox-monitor.service`
- `journalctl -u proxmox-monitor.service -f`

## Запуск приложения

### Способ 1: Прямой запуск
```bash
python3 main.py
```
(wrapper автоматически найдёт модули в `src/`)

### Способ 2: Как systemd сервис
```bash
sudo systemctl start proxmox-monitor.service
```

### Способ 3: С виртуальным окружением
```bash
source .venv/bin/activate
python3 main.py
```

## Изменение файлов конфигурации

1. **Отредактируйте конфиг:**
   ```bash
   nano config/config.yaml
   ```

2. **Перезагрузите сервис:**
   ```bash
   sudo systemctl restart proxmox-monitor.service
   ```

3. **Проверьте логи:**
   ```bash
   sudo journalctl -u proxmox-monitor.service -f
   ```

## Добавление новых модулей

Если добавляете новый модуль в `src/`:

```
src/
├── main.py
├── proxmox.py
├── alerts.py
├── telegram.py
└── new_module.py      # ← Новый модуль
```

Импортируйте в `src/main.py`:
```python
from new_module import NewClass
```

## Структура зависимостей

```
main.py (wrapper)
  └─> src/main.py
      ├─> src/proxmox.py
      ├─> src/alerts.py
      └─> src/telegram.py
```

## Где найти что

| Что нужно | Где найти |
|-----------|-----------|
| Установить проект | `scripts/install.sh` |
| Быстрый старт | `docs/QUICKSTART.md` |
| Полное руководство | `docs/README.md` |
| Конфигурировать | `config/config.yaml` |
| Справка по параметрам | `docs/CONFIG_REFERENCE.md` |
| Развёртывание | `docs/DEPLOYMENT.md` |
| Проверить здоровье | `scripts/health_check.py` |
| Запустить | `python3 main.py` |
| Логи | `journalctl -u proxmox-monitor.service` |

## Миграция

Если у вас было старое расположение, используйте этот проект. Все файлы уже организованы!

```
Старое:                 Новое:
main.py        ────>    src/main.py
proxmox.py     ────>    src/proxmox.py
alerts.py      ────>    src/alerts.py
telegram.py    ────>    src/telegram.py
*.md           ────>    docs/*.md
config.yaml    ────>    config/config.yaml
install.sh     ────>    scripts/install.sh
```

## Развёртывание с новой структурой

```bash
# 1. Установка (в /opt/proxmox-monitor)
sudo bash scripts/install.sh

# 2. Systemd автоматически найдёт файлы в правильных местах

# 3. Старт
sudo systemctl start proxmox-monitor.service

# 4. Проверка
sudo systemctl status proxmox-monitor.service
```

---

✅ **Вся документация актуальна для этой структуры!**
