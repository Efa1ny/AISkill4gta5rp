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

## Руководство по установке и подключению плагина

### 📦 Главный принцип передачи знаний ИИ-агентам

> ⚠️ **ВАЖНО: ИИ-агенту всегда передается вся папка репозитория целиком (или ZIP-архив), а не только файл `CLAUDE.md` / `AGENTS.md`!**
> 
> Файлы `CLAUDE.md` и `AGENTS.md` — это системные правила и навигатор. Сами 34 закона, индекс на 1 241 статью, судебные прецеденты ВС Mirror и консольные утилиты мгновенного поиска находятся в каталоге `gta5rp-mirror-legislation/`. Если передать агенту лишь один файл с инструкциями в отрыве от папки со справочниками и скриптами, он не сможет найти статьи и начнет выдавать ошибки либо галлюцинировать.

#### Быстрые ссылки для загрузки:
- 📥 **Скачать полный репозиторий архивом (ZIP)**: [**`AISkill4gta5rp-main.zip`**](https://github.com/Efa1ny/AISkill4gta5rp/archive/refs/heads/main.zip)
- 🐙 **Клонировать через Git**: `git clone https://github.com/Efa1ny/AISkill4gta5rp.git`

---

### Вариант 1. Установка в Google Antigravity / Gemini CLI (Рекомендуемый)

#### Способ А: Как глобальный плагин (доступен во всех проектах и чатах)
Склонируйте репозиторий прямо в каталог плагинов Antigravity:
```powershell
git clone https://github.com/Efa1ny/AISkill4gta5rp.git "$HOME\.gemini\config\plugins\gta5rp-suite"
```
После перезапуска Antigravity плагин `gta5rp-suite` появится в списке установленных расширений, а команды `/mirror-law`, `/mirror` и `/gta-law` станут доступны во всех диалогах.

#### Способ Б: Локально в конкретный проект/воркспейс
Если вы работаете в изолированной папке проекта:
```powershell
# Создайте каталог скиллов проекта и скопируйте модули:
mkdir -p .agents\skills
Copy-Item -Recurse "gta5rp-mirror-legislation" .agents\skills\
Copy-Item -Recurse "gta5rp-forum-documents" .agents\skills\
Copy-Item -Recurse "gta5rp-forum-navigation" .agents\skills\
```

---

### Вариант 2. Подключение в Claude Code (CLI в терминале)

Claude Code запускается в командной строке и оперирует файлами текущей рабочей директории.

#### Способ А: Автономная работа (запуск Claude Code прямо в папке репозитория)
1. Склонируйте репозиторий или распакуйте скачанный ZIP-архив:
   ```bash
   git clone https://github.com/Efa1ny/AISkill4gta5rp.git
   cd AISkill4gta5rp
   ```
2. Запустите Claude Code прямо в этой папке:
   ```bash
   claude
   ```
   Claude Code мгновенно подхватит конфигурацию из корневого `CLAUDE.md`, увидит локальные папки с законами и скриптами, и будет отвечать на команды `/mirror-law <запрос>` без галлюцинаций.

#### Способ Б: Встраивание в ваш существующий проект (бот, веб-сервис, парсер)
Не копируйте `CLAUDE.md` без файлов! Подключите репозиторий целиком как подпапку:
```bash
# Добавьте репозиторий как git submodule или распакуйте архив в подпапку проекта:
git submodule add https://github.com/Efa1ny/AISkill4gta5rp.git .skills/gta5rp-suite
```
После этого в `CLAUDE.md` вашего проекта достаточно указать относительные пути:
```markdown
## GTA 5 RP Mirror Legislation
When user types /mirror-law or asks about Mirror laws:
1. Search articles via: python ".skills/gta5rp-suite/gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law <код> --article <номер>
2. Consult references in: .skills/gta5rp-suite/gta5rp-mirror-legislation/references/
```

---

### Вариант 3. Подключение в веб-агенты: Claude Projects (Claude.ai) & ChatGPT (Custom GPT)

Веб-версии ИИ не имеют прямого доступа к локальному терминалу, поэтому знания передаются через встроенный механизм загрузки файлов (Knowledge):

1. **Скачайте готовый архив**: [**`AISkill4gta5rp-main.zip`**](https://github.com/Efa1ny/AISkill4gta5rp/archive/refs/heads/main.zip).
2. **Для Claude.ai (Claude Projects)**:
   - Создайте проект (например, *«Mirror Law Assistant»*).
   - В блок **Project Knowledge** загрузите скачанный ZIP-архив целиком (либо распакованные файлы из папок `references/` и `references/laws/laws_index.json`).
   - В поле **Custom Instructions** скопируйте текст из [`CLAUDE.md`](./CLAUDE.md) или [`gta5rp-mirror-legislation/SKILL.md`](./gta5rp-mirror-legislation/SKILL.md).
3. **Для ChatGPT (Custom GPTs / GPT Builder)**:
   - В настройках GPT перейдите во вкладку **Configure -> Knowledge**.
   - Загрузите `laws_index.json` и markdown-файлы законов из папки `references/laws/`.
   - В поле **Instructions** вставьте содержимое [`AGENTS.md`](./AGENTS.md).
   - Включите галочку **Code Interpreter** (чтобы ChatGPT мог писать Python-код для быстрого поиска по `laws_index.json`).

---

### Вариант 4. Подключение в Cursor, Windsurf, VS Code

1. Откройте склонированную папку `AISkill4gta5rp` в IDE через **File -> Open Folder**.
2. В файле `.cursorrules` (или настройках Project Rules) сошлитесь на файл [`AGENTS.md`](./AGENTS.md).
3. Теперь в чате Cursor Composer / Chat достаточно писать `/mirror-law <запрос>` — агент сможет напрямую вызывать терминальные команды поиска и ссылаться на строки в файлах законов.

---

## Памятка для Судей и Прокуроров (Примеры запросов)

### Для Судей:
* **Первичный аудит иска**: `«/mirror-law Проверь иск по ссылке: <URL>. Есть ли нарушения формы, подсудности или MG? Подготовь проект определения»`.
* **Оценка видеозаписи по прецеденту**: `«/mirror-law Оцени видеофиксацию ответчика по ст. 17.6 УК с учетом прецедента Верховного суда LEP-№1 (было ли 2 требования и 10 секунд?)»`.
* **Вынесение решений**: `«/mirror-law Составь проект заочного/очного решения суда по иску №...»`.
* **Судебные ордера**: `«/mirror-law Выпиши ордер ASC на арест гражданина #... по решению суда»`.

### Для Прокуроров:
* **Задержание госника при исполнении**: `«/mirror-law Госника задержали за ст. 15.6 УК. Законно ли это по ст. 8 Закона о взаимодействии силовых структур?»`.
* **Отказ от штрафа**: `«/mirror-law Гражданин нажал отмену штрафа. Проверь требования ст. 17.7 ч. 3 УК и прецедента LEP-1 (прошло ли 20 секунд?)»`.
* **Постановления и ордера**: `«/mirror-law Составь постановление об истребовании видеозаписи задержания у сотрудника LSPD [LSPD | SWAT | #12345] на 24 часа»`.
* **Снятие неприкосновенности**: `«/mirror-law Подготовь ордер типа IA в отношении руководства фракции для проведения допроса»`.

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
