# Скиллы и плагин для ИИ-агентов: GTA 5 RP Suite & Законодательство Mirror

Репозиторий модульных инструкций (Skills), справочников, офлайн-индекса законодательства и вспомогательных CLI-скриптов для обучения любых ИИ-агентов (**Google Antigravity, Claude Code, ChatGPT / Codex, Cursor, браузерных агентов и кастомных оркестраторов**) полноценной работе с проектом **GTA 5 RP** и официальной правовой базой сервера **Mirror**.

---

## Команды вызова плагина в чате (Chat Commands)

Для мгновенной активации нужного контекста в любом чате или воркспейсе используйте команды:

- **`/mirror-law <запрос>`** — правовой анализ RP-ситуаций, квалификация статей УК/ПК/СК/АК/ДК/ТК/ЭК сервера Mirror, проверка видеофиксации по прецеденту ВС LEP-№1, составление исков и жалоб.
- **`/mirror <запрос>`** — быстрый вызов контекста законодательства сервера Mirror.
- **`/gta-law <запрос>`** — общий юридический анализ GTA 5 RP.

---

## Карта модулей репозитория

Архитектура построена по принципу **Progressive Disclosure** (прогрессивного раскрытия контекста) — агент загружает в память только нужные разделы и извлекает статьи через локальный индекс, что полностью устраняет галлюцинации и экономит контекстное окно:

| Модуль (Скилл) | Статус | Назначение |
| :--- | :--- | :--- |
| **[`gta5rp-forum-navigation`](./gta5rp-forum-navigation/SKILL.md)** | Модуль 1 | **Техническая навигация по форуму XenForo 2.3 и медиа**: перемещение по серверам, разделам, подфорумам и пагинации, управление вкладками браузера, чтение тем, раскрытие спойлеров и цитат, извлечение гиперссылок («тык»/«клик»), копирование и изучение внешних медиа-файлов (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets/Drive). Поддержка обхода 403 и cookie `xf_user`. |
| **[`gta5rp-forum-documents`](./gta5rp-forum-documents/SKILL.md)** | Модуль 2 | **Анализ IC/OOC документов и судебного процесса**: полный разбор судебных исков (Верховный / Федеральный / Окружной суд), заявлений на юридическую реабилитацию, определений, заочных и очных решений, всех 10 типов ордеров (`AR`, `AS`, `ASC`, `SA`, `IA`, `PTD`, `AC`, `SE`, `MD`, `FR`), актов прокуратуры, кадрового аудита, контроль SLA (24ч / 72ч / 96ч) и проверка на смешение IC/OOC (MG). |
| **[`gta5rp-mirror-legislation`](./gta5rp-mirror-legislation/SKILL.md)** | Модуль 3 (NEW) | **Экспертная законодательная база Mirror**: 34 кодекса и закона (раздел 2181, 1241 статья), судебные прецеденты ВС (`LEP-№1`: 10с на неповиновение 17.6, 20с на отказ от штрафа 17.7), переопределения правил Гос (раздел 2164), полномочия отделов (`DB`/`CID` — рейды, `MP` — дезертиры, ст. 8 задержания госников) и глубокий разбор игрового мода (X/Z/Y, WANTED, статус SP, боди-камеры 180°, КПЗ vs ФТ, /try на автоугоне). |

---

## Структура репозитория

```text
├── README.md
├── plugin.json                            # Манифест плагина для Google Antigravity
├── AGENTS.md                              # Универсальная инструкция для ИИ-агентов
├── CLAUDE.md                              # Конфигурация для Claude Code
├── gta5rp-forum-navigation/               # Модуль 1: Навигация, чтение, ссылки и медиа
│   ├── SKILL.md
│   ├── references/
│   │   ├── xenforo-dom-and-urls.md
│   │   ├── content-reading-guide.md
│   │   └── media-and-links-handbook.md
│   └── scripts/
│       ├── parse_forum_page.py
│       └── extract_thread_content.py
├── gta5rp-forum-documents/                # Модуль 2: Аудит исков, судов и делопроизводства
│   ├── SKILL.md
│   ├── references/
│   │   ├── legal-hierarchy-and-codes.md
│   │   ├── court-and-prosecution-acts.md
│   │   └── ooc-rules-and-registries.md
│   └── scripts/
│       └── analyze_forum_document.py
└── gta5rp-mirror-legislation/             # Модуль 3: Законодательство и прецеденты Mirror
    ├── SKILL.md
    ├── references/
    │   ├── mirror-legal-hierarchy-and-gov.md
    │   ├── mirror-codes-and-qualifications.md
    │   ├── mirror-game-mechanics-and-conventions.md
    │   ├── mirror-ooc-overrides-and-precedents.md
    │   └── laws/                          # 34 закона Mirror + прецеденты + OOC правила
    │       ├── constitution.md
    │       ├── criminal_code.md
    │       ├── procedure_code.md
    │       ├── court_code.md
    │       ├── precedents_3424533.md
    │       ├── ooc_rules_mirror.md
    │       ├── laws_index.json            # Единый поисковый индекс (1241 статья)
    │       └── ... (все 34 закона)
    └── scripts/
        ├── search_mirror_law.py           # Офлайн-поиск по статьям и нормам
        └── sync_mirror_laws.py            # Синхронизация законов с форума по cookie
```

---

## Как подключить скиллы к ИИ-агенту

### 1. В Google Antigravity / Gemini CLI
* **Как плагин**: скопируйте эту папку в `~/.gemini/config/plugins/gta5rp-suite/` или используйте `customization://`.
* **Внутри рабочего проекта**: скопируйте папки модулей в `.agents/skills/`.
* **Глобально (для всех проектов)**: добавьте путь к скиллам в `~/.gemini/config/skills.json`.

### 2. В Claude Code / Codex / Cursor
* Добавьте ссылку на [`AGENTS.md`](./AGENTS.md) или [`CLAUDE.md`](./CLAUDE.md) в конфигурацию вашего проекта.

---

## Быстрый запуск CLI-утилит

Все скрипты работают на стандартной библиотеке Python 3.10+ без внешних `pip`-зависимостей:

```powershell
# 1. Поиск статьи в законах Mirror без выхода в интернет (0.05 сек):
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law УК --article 17.6
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law ПК --article 15.1
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law "взаимодействие" --article 8.1
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --precedents --query "LEP-1"
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --ooc --query "штурм"

# 2. Парсинг раздела форума (с поддержкой cookie для закрытого раздела Government):
python "gta5rp-forum-navigation/scripts/parse_forum_page.py" "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/" --cookie "585194,..."

# 3. Извлечение темы форума со всеми спойлерами и ссылками:
python "gta5rp-forum-navigation/scripts/extract_thread_content.py" "https://forum.gta5rp.com/threads/..." --cookie "585194,..."

# 4. Юридический аудит темы судебного иска или обращения в прокуратуру:
python "gta5rp-forum-documents/scripts/analyze_forum_document.py" "https://forum.gta5rp.com/threads/..." --cookie "585194,..."
```
