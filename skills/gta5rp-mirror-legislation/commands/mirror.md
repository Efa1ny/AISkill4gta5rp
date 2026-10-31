---
name: mirror
description: Быстрый поиск и цитирование статей в локальной законодательной базе сервера GTA 5 RP Mirror
argument-hint: "<номер статьи или кодекс>"
---

Найди и процитируй точную норму права из локальной базы законов сервера GTA 5 RP Mirror:

$ARGUMENTS

### ⛔ ЗАПРЕТ НА ПОИСК В ИНТЕРНЕТЕ:
НЕ ищи в интернете и НЕ открывай ссылки на `forum.gta5rp.com` (форум вернет 403 Forbidden). Все законы уже есть на диске!

### 📖 ИНСТРУКЦИЯ ПО ИЗВЛЕЧЕНИЮ СТАТЬИ:
Открой соответствующий локальный файл (`read_file` / `view`):
- Уголовный кодекс (УК): `references/laws/criminal_code.md` (или `gta5rp-mirror-legislation/references/laws/criminal_code.md`, либо `C:/Projects/gta5rp skills/gta5rp-mirror-legislation/references/laws/criminal_code.md`)
- Процессуальный кодекс (ПК): `references/laws/procedure_code.md`
- Кодекс судоустройства (СК): `references/laws/court_code.md`
- Административный кодекс (АК): `references/laws/administrative_code.md`
- Дорожный кодекс (ДК): `references/laws/traffic_code.md`
- Трудовой кодекс (ТК): `references/laws/labor_code.md`
- Закон о взаимодействии силовых структур: `references/laws/law_enforcement_interaction.md`
- Прецеденты Верховного суда: `references/laws/precedents_3424533.md`
- Сводный индекс статей: `references/laws/laws_index.json`

Выдай:
1. Полный текст диспозиции статьи из файла.
2. Подсудность (Региональная / Федеральная).
3. Количество звезд розыска `*` (1–5) и точную меру наказания (срок лишения свободы, залог, штраф).
