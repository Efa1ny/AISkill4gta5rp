# Скиллы для ИИ-агентов: Форум GTA 5 RP (`forum.gta5rp.com`)

Репозиторий модульных инструкций (Skills) и вспомогательных скриптов для обучения ИИ-агентов (Antigravity, Claude Code, Codex, браузерных агентов и кастомных оркестраторов) полноценной работе с форумом проекта **GTA 5 RP** на базе движка **XenForo 2.x**.

---

## Карта скиллов репозитория

Архитектура разделена на независимые модули по принципу **Progressive Disclosure** (прогрессивного раскрытия контекста), чтобы не перегружать контекстное окно нейросети лишними инструкциями:

| Модуль (Скилл) | Статус | Назначение |
| :--- | :--- | :--- |
| **[`gta5rp-forum-navigation`](./gta5rp-forum-navigation/SKILL.md)** | Готов | **Базовый скилл**: навигация по серверам, разделам, подфорумам и пагинации, управление вкладками браузера, чтение тем, раскрытие спойлеров и цитат, извлечение гиперссылок («тык»/«клик»), копирование и изучение внешних медиа-файлов (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets/Drive). |
| **`gta5rp-forum-documents`** | Планируется (Модуль 2) | **Анализ IC/OOC документов**: работа с законодательной базой, уставами, кодексами, разбор исковых заявлений в Верховный/Федеральный суд, обращений в прокуратуру, кадрового аудита и биографий. |
| **`gta5rp-forum-posting`** | Планируется (Модуль 3) | **Публикация и ответы**: работа с визуальным и BB-code редактором XenForo (Froala), заполнение строгих форм подачи, форматирование документов (шрифты, выравнивание, спойлеры, таблицы, вставка печатей/подписей). |

---

## Структура базового скилла `gta5rp-forum-navigation`

```text
gta5rp-forum-navigation/
├── SKILL.md                           # Главный файл инструкций и алгоритм работы для ИИ-агента
├── references/
│   ├── xenforo-dom-and-urls.md        # Справочник URL-паттернов, DOM-селекторов XenForo 2.x, вкладок и пагинации
│   ├── content-reading-guide.md       # Правила чтения постов, раскрытия спойлеров, цитат, таблиц и истории правок
│   └── media-and-links-handbook.md    # Гайд по гиперссылкам и внешним медиа (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets)
└── scripts/
    ├── parse_forum_page.py            # CLI-скрипт парсинга разделов форума (хлебные крошки, подфорумы, закрепленные и обычные темы)
    └── extract_thread_content.py      # CLI-скрипт извлечения всех постов темы, текста из спойлеров/цитат, ссылок и медиа
```

---

## Как подключить скилл к ИИ-агенту

### 1. В Google Antigravity / Gemini CLI
Вы можете подключить скилл одним из способов:
* **Внутри рабочего проекта**: скопируйте папку `gta5rp-forum-navigation` в `.agents/skills/gta5rp-forum-navigation`.
* **Глобально (для всех проектов)**: скопируйте папку `gta5rp-forum-navigation` в `C:\Users\<User>\.gemini\config\skills\gta5rp-forum-navigation` или укажите путь к `C:\Projects\gta5rp skills` в конфигурационном файле `skills.json`.

### 2. В Claude Code / Codex / Cursor
* Сошлитесь на [`gta5rp-forum-navigation/SKILL.md`](./gta5rp-forum-navigation/SKILL.md) в вашем `AGENTS.md` или `CLAUDE.md`, либо добавьте папку в директорию скиллов агента.

### 3. Быстрый запуск вспомогательных утилит вручную

Оба скрипта в `scripts/` написаны на стандартной библиотеке Python 3.10+ и не требуют установки сторонних пакетов:

```powershell
# Парсинг раздела форума (вывод в читаемом виде или --json)
python "C:\Projects\gta5rp skills\gta5rp-forum-navigation\scripts\parse_forum_page.py" "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/"

# Полное извлечение постов, спойлеров, ссылок и медиа из темы
python "C:\Projects\gta5rp skills\gta5rp-forum-navigation\scripts\extract_thread_content.py" "https://forum.gta5rp.com/threads/..."
```
