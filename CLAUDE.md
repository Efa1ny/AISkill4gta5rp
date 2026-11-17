# Claude Code Instructions (GTA 5 RP Suite & Mirror Legislation)

This repository provides agentic tools, skills, and the full legislative and judicial database for the GTA 5 RP **Mirror** server.

> **ВАЖНО / CRITICAL**:
> Этот конфигурационный файл работает **в связке со всей папкой репозитория** (`skills/`, `commands/`, `references/`).
> Не копируйте `CLAUDE.md` в изоляции в пустую папку! Claude Code выполняет реальные поисковые скрипты и читает оффлайн-справочники. Для работы агенту нужна вся папка (склонированная через `git clone` или распакованная из ZIP-архива).

## Commands / Triggers
- `/mirror-on [judge|prosecutor]`: Включить постоянный правовой режим Mirror на весь чат (тумблер ВКЛ; аргумент — профиль судьи или прокурора). Все дальнейшие вопросы по умолчанию оцениваются по законам Mirror из локальных файлов без поиска в интернете.
- `/mirror-off`: Выключить постоянный режим Mirror и вернуться к обычному диалогу (тумблер ВЫКЛ).
- `/check-claim <URL темы/сообщения на форуме>`: Процессуальный аудит иска/обращения по ссылке: форма, паспорт, пошлина, сроки SLA, детектор MG (Модуль 2).
- `/read-thread <URL темы/сообщения на форуме>`: Разбор темы форума XenForo по ссылке: раскрытие спойлеров и ссылок на видеозаписи (Модуль 1).
- `/mirror-law <статья или ситуация>`: Дословная цитата статьи или разовый правовой анализ RP-ситуации, задержания, видеофиксации или иска (Модуль 3).

## Modules Overview
- `skills/gta5rp-forum-navigation/`: XenForo 2.3 parser, hidden spoiler/quote expander, media extractor (Imgur, Yapx, YouTube, Google Docs/Sheets).
- `skills/gta5rp-forum-documents/`: Court claim audit, SLA tracker (24h/72h/96h), fee/passport checks, MetaGaming detector.
- `skills/gta5rp-mirror-legislation/`: Complete Mirror legislation (34 laws/codes), OOC overrides, game mechanics.

## Quick CLI Search (Zero Hallucination)
Always verify article numbers and sanctions before answering:
```bash
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law УК --article 15.5
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law УК --article 17.6
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law СК --article 15.11
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law ПК --article 15.1
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law "взаимодействие" --article 8.1
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --law ПК --article 1.4.1
python skills/gta5rp-mirror-legislation/scripts/search_mirror_law.py --ooc --query "штурм"
```

## Key Server Rules & Conventions
1. OOC server rules always override IC legislation in case of conflict.
2. Cite only statutes from the local base. Art. 17.6 УК: lawful demand (ПК 1.4) given twice, reasonable time (ПК 1.5), future-directed demands are unlawful, the officer proves lawfulness (ПК 1.4.1); failing a demand to stop an administrative offence is АК 5.2, not 17.6; refusing to remove a mask is 17.6 at once (note to АК 6.7). Art. 17.7 УК: ignoring the ticket for 20s (the article's own note).
3. State employees on duty can only be detained for violent/felony crimes explicitly listed in art. 8 of Law on Law Enforcement Interaction (never on the spot for art. 15.1 / 15.6).
4. Only DB (LSPD/LSSD) and CID (FIB) may write raid case files. Only MP (NG) may patrol for deserters.
5. In-game mechanics: Handcuffs (`X`), Escort (`Z`), WANTED tag in Green Zones without mask, SP secret identity, 180° bodycam from 24/7, virtual parking protection.

## Maintaining the plugin
- Edit only `commands/` and `skills/`, then run `python scripts/sync_copies.py`: the top-level module folders and `skills/gta5rp-mirror-legislation/commands/` are generated copies.
- Update laws: `python skills/gta5rp-mirror-legislation/scripts/sync_mirror_laws.py` (needs the `GTA5RP_XF_USER` cookie or `--html-dir`), review `git diff`, push to `main`. The script bumps the patch version in both `plugin.json`; bump it yourself after manual edits — the Claude Code marketplace (`.claude-plugin/marketplace.json`) only ships updates when `version` changes.
