# Скиллы для ИИ-агентов: Форум GTA 5 RP (`forum.gta5rp.com`)

Репозиторий модульных инструкций (Skills) и вспомогательных скриптов для обучения ИИ-агентов (Antigravity, Claude Code, Codex, браузерных агентов и кастомных оркестраторов) полноценной работе с форумом проекта **GTA 5 RP** на базе движка **XenForo 2.x**.

---

## Карта скиллов репозитория

Архитектура разделена на два независимых модуля по принципу **Progressive Disclosure** (прогрессивного раскрытия контекста), чтобы минимизировать потребление токенов и не перегружать контекстное окно нейросети:

| Модуль (Скилл) | Статус | Назначение |
| :--- | :--- | :--- |
| **[`gta5rp-forum-navigation`](./gta5rp-forum-navigation/SKILL.md)** | Готов (Модуль 1) | **Базовый скилл (Техническая навигация и медиа)**: перемещение по серверам, разделам, подфорумам и пагинации, управление вкладками браузера, чтение тем, раскрытие спойлеров и цитат, извлечение гиперссылок («тык»/«клик»), копирование и изучение внешних медиа-файлов (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets/Drive). |
| **[`gta5rp-forum-documents`](./gta5rp-forum-documents/SKILL.md)** | Готов (Модуль 2) | **Анализ IC/OOC документов и делопроизводства**: работа с законодательной базой (иерархия НПА, кодексы, уставы), полный разбор судебных исков (Верховный / Федеральный / Окружной суд), заявлений на юридическую реабилитацию, определений, заочных и очных решений, ордеров (`IA`, `AS`, `ASC`, `RI`, `SA`), актов прокуратуры, уголовных дел (Case Files), кадрового аудита и проверка на смешение IC/OOC (MG). |

---

## Структура репозитория

```text
├── README.md
├── gta5rp-forum-navigation/               # Модуль 1: Навигация, чтение, ссылки и медиа
│   ├── SKILL.md
│   ├── references/
│   │   ├── xenforo-dom-and-urls.md
│   │   ├── content-reading-guide.md
│   │   └── media-and-links-handbook.md
│   └── scripts/
│       ├── parse_forum_page.py
│       └── extract_thread_content.py
└── gta5rp-forum-documents/                # Модуль 2: Анализ IC/OOC документов, судов и законов
    ├── SKILL.md
    ├── references/
    │   ├── legal-hierarchy-and-codes.md
    │   ├── court-and-prosecution-acts.md
    │   └── ooc-rules-and-registries.md
    └── scripts/
        └── analyze_forum_document.py
```

---

## Как подключить скиллы к ИИ-агенту

### 1. В Google Antigravity / Gemini CLI
* **Внутри рабочего проекта**: скопируйте папки `gta5rp-forum-navigation` и `gta5rp-forum-documents` в `.agents/skills/`.
* **Глобально (для всех проектов)**: скопируйте обе папки в `C:\Users\<User>\.gemini\config\skills\` или укажите путь к этому репозиторию в `skills.json`.

### 2. В Claude Code / Codex / Cursor
* Сошлитесь на [`gta5rp-forum-navigation/SKILL.md`](./gta5rp-forum-navigation/SKILL.md) и [`gta5rp-forum-documents/SKILL.md`](./gta5rp-forum-documents/SKILL.md) в вашем `AGENTS.md` или `CLAUDE.md`.

### 3. Быстрый запуск CLI-утилит вручную

Все скрипты написаны на стандартной библиотеке Python 3.10+ и не требуют установки сторонних зависимостей:

```powershell
# 1. Парсинг списка тем и подразделов форума
python "gta5rp-forum-navigation/scripts/parse_forum_page.py" "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/"

# 2. Извлечение всех постов, спойлеров, ссылок и медиа из темы
python "gta5rp-forum-navigation/scripts/extract_thread_content.py" "https://forum.gta5rp.com/threads/..."

# 3. Юридический и структурный анализ темы-иска или документа (стороны, Static ID, статьи, хронология актов, чек-лист приложений)
python "gta5rp-forum-documents/scripts/analyze_forum_document.py" "https://forum.gta5rp.com/threads/..."
```
