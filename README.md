# Скиллы и плагин для ИИ-агентов: GTA 5 RP Suite & Законодательство Mirror

Репозиторий модульных инструкций (Skills), справочников, офлайн-индекса законодательства и вспомогательных CLI-скриптов для обучения любых ИИ-агентов (**Google Antigravity, Claude Code, ChatGPT / Codex, Cursor, браузерных агентов и кастомных оркестраторов**) полноценной работе с проектом **GTA 5 RP** и официальной правовой базой сервера **Mirror**.

---

## Команды вызова плагина в чате (Chat Commands)

### 🔘 Постоянный режим-тумблер (Включить один раз на весь диалог)
- **`/mirror-on`** — **включает постоянный правовой режим Mirror на весь текущий чат**. После этой команды агент фиксирует контекст всех 35 законов и игровых механик: вы можете задавать любые вопросы обычным текстом (*«что такое 15.5 УК?»*, *«оцени откат задержания»*, *«законно ли изъяли оружие?»*) без повторного ввода команд!
- **`/mirror-off`** — выключает правовой режим и возвращает агента к стандартному нейтральному общению.
- **`/mirror-review <закон, статья или тема>`** — разбор самих законов: коллизии, пробелы, неясные формулировки, битые отсылки (`check_law_refs.py`), проект поправок и черновик законодательной инициативы для обсуждения (режим держится до `/mirror-off`).

### ⚡ Разовые команды по модулям системы
- **`/check-claim <URL, сохранённый HTML или текст иска>`** — процессуальный аудит иска/обращения: проверка формы, ксерокопии паспорта, оплаты пошлины, сроков давности по СК (72ч / 48ч за незаконное задержание), поиск MetaGaming (MG) и готовый проект определения суда (Модуль 2).
- **`/read-thread <URL, сохранённый HTML или текст темы>`** — технический разбор темы форума XenForo: сбор сообщений, раскрытие спойлеров `[SPOILER]` и группировка внешних ссылок на видеозаписи (YouTube/Rutube/Yapx/Imgur) (Модуль 1).
- **`/mirror-law <статья или ситуация>`** — дословная цитата статьи (например, `/mirror-law 17.6 УК`) или правовой анализ ситуации: квалификация по УК/ПК/СК/АК/ДК/ТК/ЭК сервера Mirror, проверка видеофиксации и законности требований сотрудников (Модуль 3).

---

## Карта модулей репозитория

Архитектура построена по принципу **Progressive Disclosure** (прогрессивного раскрытия контекста) — агент загружает в память только нужные разделы и извлекает статьи через локальный индекс, что полностью устраняет галлюцинации и экономит контекстное окно:

| Модуль (Скилл) | Статус | Назначение |
| :--- | :--- | :--- |
| **[`gta5rp-forum-navigation`](./gta5rp-forum-navigation/SKILL.md)** | Модуль 1 | **Техническая навигация по форуму XenForo 2.3 и медиа**: перемещение по серверам, разделам, подфорумам и пагинации, управление вкладками браузера, чтение тем, раскрытие спойлеров и цитат, извлечение гиперссылок («тык»/«клик»), копирование и изучение внешних медиа-файлов (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets/Drive). Поддержка обхода 403 и cookie `xf_user`. |
| **[`gta5rp-forum-documents`](./gta5rp-forum-documents/SKILL.md)** | Модуль 2 | **Анализ IC/OOC документов и судебного процесса**: полный разбор судебных исков (Верховный / Окружной суд), заявлений на юридическую реабилитацию, определений, заочных и очных решений, всех 10 типов ордеров (`AR`, `AS`, `ASC`, `SA`, `IA`, `PTD`, `AC`, `SE`, `MD`, `FR`), актов прокуратуры, кадрового аудита, контроль SLA (24ч / 72ч / 96ч) и проверка на смешение IC/OOC (MG). |
| **[`gta5rp-mirror-legislation`](./gta5rp-mirror-legislation/SKILL.md)** | Модуль 3 (NEW) | **Экспертная законодательная база Mirror**: 35 кодексов и законов (раздел 2181, 1862 статья), переопределения правил Гос (раздел 2164), полномочия отделов (`DB`/`CID` — рейды, `MP` — дезертиры, ст. 8 задержания госников) и глубокий разбор игрового мода (X/Z/Y, WANTED, статус SP, боди-камеры 180°, КПЗ vs ФТ, /try на автоугоне). |

---

## Структура репозитория

```text
├── README.md
├── plugin.json                            # Манифест плагина для Google Antigravity
├── .claude-plugin/plugin.json             # Манифест плагина для Anthropic Claude Desktop
├── AGENTS.md                              # Универсальная инструкция для ИИ-агентов
├── CLAUDE.md                              # Конфигурация для Claude Code
├── commands/                              # Слэш-команды (канон; .md — Claude, .toml — Gemini CLI)
│   ├── mirror-on.md / mirror-off.md
│   ├── mirror-law.md
│   ├── check-claim.md
│   └── read-thread.md
├── scripts/sync_copies.py                 # Синхронизация дублей: commands/ и skills/ → копии модулей
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
└── gta5rp-mirror-legislation/             # Модуль 3: Законодательство Mirror
    ├── SKILL.md
    ├── references/
    │   ├── mirror-legal-hierarchy-and-gov.md
    │   ├── mirror-codes-and-qualifications.md
    │   ├── mirror-game-mechanics-and-conventions.md
    │   ├── mirror-ooc-overrides.md
    │   └── laws/                          # 35 законов Mirror + OOC правила
    │       ├── constitution.md
    │       ├── criminal_code.md
    │       ├── procedure_code.md
    │       ├── court_code.md
    │       ├── ooc_rules_mirror.md
    │       ├── laws_index.json            # Метаданные НПА: алиасы, редакции, ID тем (тексты — в *.md)
    │       └── ... (все 35 законов)
    └── scripts/
        ├── search_mirror_law.py           # Офлайн-поиск по статьям и нормам
        ├── sync_mirror_laws.py            # Обновление законов с форума (см. «Обновление законодательной базы»)
        └── build_laws_index.py            # Пересборка laws_index.json (--check — проверка для CI)
```

---

## Руководство по установке и подключению плагина

### 📦 Главный принцип передачи знаний ИИ-агентам

> ⚠️ **ВАЖНО: ИИ-агенту всегда передается вся папка репозитория целиком (или ZIP-архив), а не только файл `CLAUDE.md` / `AGENTS.md`!**
> 
> Файлы `CLAUDE.md` и `AGENTS.md` — это системные правила и навигатор. Сами 35 законов, индекс на 1 862 статью, аудит судебных исков и инструменты форума находятся внутри папок `skills/` и `commands/`. Если передать агенту лишь один файл с инструкциями в отрыве от папки со справочниками и скриптами, он не сможет найти статьи и начнет выдавать ошибки либо галлюцинировать.

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
После перезапуска Antigravity плагин `gta5rp-suite` появится в списке установленных расширений, а команды `/mirror-on`, `/mirror-law`, `/check-claim` и `/read-thread` станут доступны во всех диалогах.

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

### Вариант 2. Подключение в Claude Code (CLI в терминале и вкладка Code в Claude Desktop)

#### Способ А (рекомендуемый): маркетплейс плагинов с автообновлением
Репозиторий — маркетплейс Claude Code (`.claude-plugin/marketplace.json`). Установка в сессии Claude Code:
```
/plugin marketplace add Efa1ny/AISkill4gta5rp
/plugin install gta5rp-suite@efa1ny-gta5rp
```
Или одной командой в терминале: `claude plugin install gta5rp-suite --marketplace Efa1ny/AISkill4gta5rp`.

**Включи автообновление один раз**: `/plugin` → **Marketplaces** → `efa1ny-gta5rp` → **Enable auto-update**. После этого каждая новая версия с GitHub ставится сама при запуске Claude Code. Без автообновления обнови вручную: `/plugin marketplace update efa1ny-gta5rp`.

> Если у вас нет SSH-ключа GitHub и установка падает на клонировании, задайте переменную окружения `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.

Команды плагина вызываются с префиксом плагина: `/gta5rp-suite:mirror-on`, `/gta5rp-suite:mirror-law` и т. д.

#### Способ Б: Автономная работа (запуск Claude Code прямо в папке репозитория)
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

#### Способ В: Встраивание в ваш существующий проект (бот, веб-сервис, парсер)
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
   - В блок **Project Knowledge** загрузите скачанный ZIP-архив целиком (либо распакованные файлы из папок `references/` и `references/laws/`).
   - В поле **Custom Instructions** скопируйте текст из [`CLAUDE.md`](./CLAUDE.md) или [`gta5rp-mirror-legislation/SKILL.md`](./gta5rp-mirror-legislation/SKILL.md).
3. **Для ChatGPT (Custom GPTs / GPT Builder)**:
   - В настройках GPT перейдите во вкладку **Configure -> Knowledge**.
   - Загрузите markdown-файлы законов и `laws_index.json` из папки `references/laws/`, а также `search_mirror_law.py` и `build_laws_index.py` из `scripts/`.
   - В поле **Instructions** вставьте содержимое [`AGENTS.md`](./AGENTS.md).
   - Включите галочку **Code Interpreter** (чтобы ChatGPT запускал `search_mirror_law.py` для поиска статей по md-файлам).

---

### Вариант 4. Подключение в официальные десктопные приложения (Claude Desktop & ChatGPT Desktop)

Если вы используете официальные приложения Claude или ChatGPT для Windows / macOS:

#### 1. Claude Desktop (Приложение для Windows / Mac)

В десктопном клиенте Claude плагин устанавливается **целиком из одного архива**:

* **Способ А: Встроенная загрузка плагина целиком (Настройки -> Плагины -> Загрузить плагин) — РЕКОМЕНДУЕМЫЙ**:
  Благодаря единой архитектуре манифеста `.claude-plugin/plugin.json` и каталога `skills/`, весь комплекс со всеми 3 модулями, 35 законовми и командами устанавливается **одним единым ZIP-файлом без разделения по частям**:
  1. Скачайте полный архив репозитория с GitHub: [**`AISkill4gta5rp-main.zip`**](https://github.com/Efa1ny/AISkill4gta5rp/archive/refs/heads/main.zip) (или соберите локально через `py scripts/package_bundle.py`).
  2. В приложении Claude Desktop откройте **Настройки (Settings)** (иконка шестеренки в нижнем левом углу).
  3. В боковом меню перейдите в раздел **Плагины (Plugins)**.
  4. В правом верхнем углу нажмите кнопку **`+ Добавить`** -> выберите **«Загрузить плагин»**.
  5. Перетащите скачанный ZIP-архив целиком в область «Перетащите сюда файлы плагинов» и нажмите кнопку **«Загрузить»**.
  6. Плагин установится единым пакетом **`gta5rp-suite`** и появится в блоке **«Создано вами»**.
  7. **Сразу доступны все возможности комплекса**:
     - **`/mirror-on`** — включить постоянный правовой режим Mirror на весь текущий чат;
     - **`/check-claim <URL темы на форуме>`** — процессуальный аудит иска, проверка пошлины, SLA и MG;
     - **`/read-thread <URL темы на форуме>`** — разбор темы форума XenForo, раскрытие спойлеров и ссылок на видео;
     - **`/mirror-law <статья или ситуация>`** — цитата статьи или разовый юридический анализ ситуации.

* **Способ Б: Через Claude Projects (Синхронизация с аккаунтом Pro / Team / Enterprise)**:
  1. В левой панели приложения Claude Desktop откройте раздел **Projects** (Проекты) и создайте проект, например `GTA 5 RP Mirror Law`.
  2. В блоке **Project Knowledge** нажмите **Add Content** -> перетащите скачанный с GitHub ZIP-архив целиком [**`AISkill4gta5rp-main.zip`**](https://github.com/Efa1ny/AISkill4gta5rp/archive/refs/heads/main.zip).
  3. В поле **Project Instructions** скопируйте и вставьте текст из файла [`CLAUDE.md`](./CLAUDE.md).
  4. Любой диалог внутри этого проекта будет автоматически владеть законодательной базой Mirror.

* **Способ В: Через локальный MCP-сервер (Model Context Protocol — чтение с диска в реальном времени)**:
  Claude Desktop умеет читать локальные файлы прямо на вашем компьютере:
  1. Откройте файл конфигурации Claude Desktop:
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  2. Добавьте стандартный MCP-сервер файловой системы, указав путь к папке репозитория:
     ```json
     {
       "mcpServers": {
         "mirror-legislation": {
           "command": "npx",
           "args": [
             "-y",
             "@modelcontextprotocol/server-filesystem",
             "C:\\Projects\\gta5rp skills"
           ]
         }
       }
     }
     ```
  3. Перезапустите Claude Desktop — в интерфейсе появится иконка MCP-инструментов, и Claude сможет самостоятельно читать статьи и законы с вашего диска.

* **Способ Г: Быстрый Drag-and-Drop в любой диалог**:
  Если нужно срочно разобрать ситуацию без установки плагина:
  - Перетащите файл архива `AISkill4gta5rp-main.zip` прямо в поле ввода сообщения.
  - Напишите: `«Изучи прикрепленный архив с законами Mirror. В дальнейшем при команде /mirror-law руководствуйся ими. Ситуация: ...»`.

---

#### 2. ChatGPT Desktop (Приложение для Windows / Mac)

В десктопном клиенте ChatGPT работа строится следующим образом:

* **Способ А: Через Custom GPT (Самый стабильный и постоянный вариант)**:
  Custom GPT, созданный в вашем аккаунте через браузер, **автоматически появляется в левой панели десктопного приложения ChatGPT**:
  1. В веб-версии перейдите в **Explore GPTs** -> **Create**.
  2. Во вкладке **Configure**:
     - **Name**: `Mirror Law Assistant`
     - **Instructions**: вставьте содержимое [`AGENTS.md`](./AGENTS.md).
     - **Knowledge**: загрузите файлы из папки `references/laws/` и скрипты `search_mirror_law.py`, `build_laws_index.py` (или архив `AISkill4gta5rp-Mirror.zip`).
     - **Capabilities**: обязательно включите галочку **Code Interpreter & Data Analysis**.
  3. Сохраните GPT (**Save**).
  4. Откройте десктопное приложение **ChatGPT Desktop** на Windows или Mac — ваш созданный ассистент будет доступен в боковом меню в 1 клик.

* **Способ Б: Разовый анализ через Drag & Drop архива в чат**:
  1. Перетащите скачанный файл `AISkill4gta5rp-Mirror.zip` мышкой в поле ввода чата ChatGPT Desktop.
  2. Отправьте запрос:
     ```text
     Распакуй прикрепленный архив со справочниками и законами сервера Mirror.
     Принимай команду /mirror-law как триггер для правового анализа.
     Ситуация: [опишите RP-ситуацию или вопрос]
     ```
  3. ChatGPT Desktop через встроенный Code Interpreter распакует архив во временную песочницу, выполнит поиск скриптом `search_mirror_law.py` по md-файлам законов и предоставит квалификацию со ссылками на статьи.

---

### Вариант 5. Подключение в Cursor, Windsurf, VS Code

1. Откройте склонированную папку `AISkill4gta5rp` в IDE через **File -> Open Folder**.
2. В файле `.cursorrules` (или настройках Project Rules) сошлитесь на файл [`AGENTS.md`](./AGENTS.md).
3. Теперь в чате Cursor Composer / Chat достаточно писать `/mirror-law <запрос>` — агент сможет напрямую вызывать терминальные команды поиска и ссылаться на строки в файлах законов.

---

## Памятка для Судей и Прокуроров (Примеры запросов)

### Для Судей:
* **Первичный аудит иска**: `«/mirror-law Проверь иск по ссылке: <URL>. Есть ли нарушения формы, подсудности или MG? Подготовь проект определения»`.
* **Оценка видеозаписи**: `«/mirror-law Оцени видеофиксацию ответчика по ст. 17.6 УК (были ли 2 законных требования и разумное время по ст. 1.5 ПК?)»`.
* **Вынесение решений**: `«/mirror-law Составь проект заочного/очного решения суда по иску №...»`.
* **Судебные ордера**: `«/mirror-law Выпиши ордер ASC на арест гражданина #... по решению суда»`.

### Для Прокуроров:
* **Задержание госника при исполнении**: `«/mirror-law Госника задержали за ст. 15.6 УК. Законно ли это по ст. 8 Закона о взаимодействии силовых структур?»`.
* **Отказ от штрафа**: `«/mirror-law Гражданин нажал отмену штрафа. Проверь требования ст. 17.7 УК (прошло ли 20 секунд?)»`.
* **Постановления и ордера**: `«/mirror-law Составь постановление об истребовании видеозаписи задержания у сотрудника LSPD [LSPD | SWAT | #12345] на 24 часа»`.
* **Снятие неприкосновенности**: `«/mirror-law Подготовь ордер типа IA в отношении руководства фракции для проведения допроса»`.

---

## Обновление законодательной базы

База законов зашита в плагин, поэтому обновление идёт через GitHub: мейнтейнер обновляет репозиторий, пользователи переустанавливают плагин.

### Для мейнтейнера
1. Скачай свежие редакции с форума (нужен cookie `xf_user` аккаунта с доступом к разделу 2181):
   ```powershell
   $env:GTA5RP_XF_USER = "<id>,<токен>"
   python skills/gta5rp-mirror-legislation/scripts/sync_mirror_laws.py            # все 35 НПА
   python skills/gta5rp-mirror-legislation/scripts/sync_mirror_laws.py --only criminal_code procedure_code
   ```
   Если форум отдаёт скрипту 403 — сохрани страницы тем из браузера как `thread_<ID темы>.html` и запусти с `--html-dir <папка>`.
   Скрипт перезаписывает только изменившиеся `references/laws/*.md`, пересобирает `laws_index.json`, поднимает patch-версию в обоих `plugin.json` и обновляет копии модулей. Тема, которая не скачалась, остаётся как была.
2. Проверь `git diff`: номера статей, санкции, дату редакции в шапке файла.
3. Если правил вручную `commands/` или `skills/` — синхронизируй дубли: `python scripts/sync_copies.py` (`--check` — только проверка). Правил md законов руками — пересобери индекс: `python skills/gta5rp-mirror-legislation/scripts/build_laws_index.py`. Всё это проверяет CI (`.github/workflows/check.yml`) на каждом PR.
4. Закоммить и запушь в `main`. Если менял что-то руками без скрипта — сам подними `version` в `plugin.json` и `.claude-plugin/plugin.json`: маркетплейс Claude Code ставит обновление только при смене версии.

### Для пользователей
- **Claude Desktop**: скачай свежий [ZIP](https://github.com/Efa1ny/AISkill4gta5rp/archive/refs/heads/main.zip) и загрузи плагин заново (Настройки → Плагины). Версия в карточке плагина должна совпасть с `plugin.json` на GitHub.
- **Claude Code через маркетплейс**: обновляется сам, если включено автообновление (см. «Вариант 2»), иначе `/plugin marketplace update efa1ny-gta5rp`.
- **Antigravity / Gemini CLI / Claude Code из папки** (установка через `git clone`): `git pull` в папке плагина.
- **Claude Projects / Custom GPT**: замени загруженный архив или файлы `references/laws/` на свежие.

---

## Быстрый запуск CLI-утилит

Все скрипты работают на стандартной библиотеке Python 3.10+ без внешних `pip`-зависимостей:

```powershell
# 1. Поиск статьи в законах Mirror без выхода в интернет (0.05 сек):
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law УК --article 17.6
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law ПК --article 15.1
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law "взаимодействие" --article 8.1
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --law ПК --article 1.4.1
python "gta5rp-mirror-legislation/scripts/search_mirror_law.py" --ooc --query "штурм"

# 1а. Битые отсылки между статьями (ссылки на несуществующие статьи):
python "gta5rp-mirror-legislation/scripts/check_law_refs.py" --law СК

# Форум закрыт для гостей: без входа виден только раздел «Дополнительные правила сервера».
# Суды, прокуратура и законы — только с cookie xf_user (DevTools → Application → Cookies → xf_user),
# лучше через переменную окружения: $env:GTA5RP_XF_USER = "<id>,<токен>". Без доступа скрипты
# завершаются с кодом 2 и подсказкой; альтернатива — сохранённая страница темы и --file <путь>.

# 2. Парсинг раздела форума:
python "gta5rp-forum-navigation/scripts/parse_forum_page.py" "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/" --cookie "<id>,<токен>"

# 3. Извлечение темы форума со всеми спойлерами и ссылками:
python "gta5rp-forum-navigation/scripts/extract_thread_content.py" "https://forum.gta5rp.com/threads/..." --cookie "<id>,<токен>"

# 4. Юридический аудит темы судебного иска или обращения в прокуратуру:
python "gta5rp-forum-documents/scripts/analyze_forum_document.py" "https://forum.gta5rp.com/threads/..." --cookie "<id>,<токен>"
```
