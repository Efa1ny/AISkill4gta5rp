# Руководство по чтению тем, спойлеров, цитат и таблиц (`content-reading-guide.md`)

Когда ты открываешь тему на форуме GTA 5 RP (`/threads/<slug>.<id>/`), твоя задача — извлечь полную, неискаженную информацию из каждого сообщения, не потеряв скрытые блоки, вложенные цитаты, таблицы и метаданные.

---

## 1. Анатомия страницы темы

* **Заголовок темы**: `h1.p-title-value` (содержит префикс `span.label`, если он установлен, и само название темы).
* **Автор темы и дата создания шапки**: блок `.p-description` под заголовком (`a.username`, `time.u-dt[datetime]`).
* **Контейнер всех сообщений на странице**: `div.block--messages div.block-body.js-replyNewMessageContainer`.
* **Отдельное сообщение (пост)**: тег `<article class="message message--post js-post js-inlineModContainer" data-author="..." data-content="post-1234567" id="js-post-1234567">`.

---

## 2. Метаданные каждого поста (`article.message--post`)

При чтении темы **всегда фиксируй метаданные каждого поста**, так как в РП-процессах (судебные иски, жалобы, приказы, кадровый аудит) критически важно, **кто именно** написал сообщение, **в какое время** и **редактировалось ли оно позже**:

| Поле | Селектор / Атрибут внутри `article.message--post` | Особенности |
| :--- | :--- | :--- |
| **ID поста** | Атрибут `data-content="post-9876543"` или `id="js-post-9876543"` | Уникальный идентификатор сообщения в базе форума |
| **Порядковый номер в теме** | `.message-attribution-opposite li:last-child a` | Текст вида `#1`, `#2`, `#3`. Пост `#1` — это всегда исходный документ/заявление автора темы |
| **Прямая ссылка на пост** | `.message-attribution-opposite a[href*="/post-"]` | Позволяет сослаться на конкретный ответ в теме |
| **Никнейм автора** | Атрибут `data-author` у `<article>` или `.message-userDetails .message-name .username` | Имя форумного аккаунта |
| **Нестандартное звание / Должность** | `.message-userDetails h5.userTitle` | Часто содержит IC-должность игрока (например, `Supreme Judge`, `Attorney General`, `Leader LSPD`) |
| **Баннер роли (Плашка)** | `.message-userDetails .userBanner strong` | Официальная форумная краска/роль (например, `Администратор`, `Куратор фракции`, `Лидер`, `Судья`) |
| **Точная дата и время публикации** | `header.message-attribution time.u-dt` → атрибут `datetime` | Всегда извлекай ISO-строку из `datetime` (например, `2026-08-14T17:54:46+0300`), а не видимый текст (`Пятница`, `42 мин. назад`) |
| **Отметка о последнем редактировании** | `div.message-lastEdit time.u-dt` → атрибут `datetime` | Показывает, когда пост был изменен после публикации. Если блок `.message-lastEdit` отсутствует — пост не редактировался (или был отредактирован в первые минуты) |

---

## 3. Чтение основного текста поста (`div.bbWrapper`)

Весь пользовательский контент сообщения находится внутри:
```css
article.message--post div.message-userContent div.bbWrapper
```

На форуме GTA 5 RP активно используются сложные конструкции BB-кодов. Ниже описано, как правильно читать каждую из них.

---

## 4. Работа со скрытым и свернутым контентом

### 4.1. Спойлеры (`[SPOILER]` / `.bbCodeSpoiler`)
В спойлеры прячут:
* Статьи законов и главы уставов;
* Длинные списки доказательств, таймкоды видео, скриншоты документов;
* Формы подачи заявлений (код шаблона, который нужно скопировать);
* Историю изменений документа (Changelog).

**HTML-структура спойлера в XenForo 2.x**:
```html
<div class="bbCodeSpoiler">
    <button type="button" class="bbCodeSpoiler-button button--longText button" data-xf-click="toggle">
        <span class="button-text">
            <span>Спойлер: <span class="bbCodeSpoiler-button-title">Ксерокопия документов</span></span>
        </span>
    </button>
    <div class="bbCodeSpoiler-content">
        <div class="bbCodeBlock bbCodeBlock--spoiler">
            <div class="bbCodeBlock-content">
                <!-- СКРЫТЫЙ КОНТЕНТ ЗДЕСЬ -->
            </div>
        </div>
    </div>
</div>
```

**Правила для ИИ-агента**:
1. **Если ты читаешь HTML/DOM напрямую (или через скрипт `extract_thread_content.py`)**:
   * Содержимое `.bbCodeSpoiler-content` **уже загружено в DOM**! Тебе не нужно делать сетевых запросов, чтобы прочитать текст или ссылки внутри спойлера — просто извлекай текст и теги `<a>`/`<img>` из `.bbCodeSpoiler-content`, предварительно прочитав заголовок спойлера из `.bbCodeSpoiler-button-title`.
2. **Если ты смотришь на страницу глазами браузерного агента (по скриншотам viewport)**:
   * По умолчанию `.bbCodeSpoiler-content` скрыт через CSS (`display: none; opacity: 0`).
   * Найди все элементы `button.bbCodeSpoiler-button` и выполни по ним клик (или вызови в консоли/Playwright: `document.querySelectorAll('.bbCodeSpoiler-button').forEach(btn => btn.click())`), чтобы раскрыть все спойлеры разом перед снятием скриншота или визуальным чтением!
   * Учитывай **вложенные спойлеры** (спойлер внутри спойлера в законодательной базе): после первого раскрытия проверь, не появились ли внутри новые закрытые `.bbCodeSpoiler-button`.

---

### 4.2. Цитаты и свернутые блоки (`[QUOTE]` / `blockquote.bbCodeBlock--quote`)
Когда судья, прокурор или игрок отвечает на предыдущее сообщение, он цитирует его. Если цитата длиннее ~150px, XenForo сворачивает ее и добавляет градиентную шторку «Нажмите для раскрытия...».

**HTML-структура цитаты**:
```html
<blockquote class="bbCodeBlock bbCodeBlock--expandable bbCodeBlock--quote js-expandWatch is-expandable" data-quote="sena_creator" data-source="post: 9812300">
    <div class="bbCodeBlock-title">
        <a href="/goto/post?id=9812300" class="bbCodeBlock-sourceJump" data-xf-click="attribution">sena_creator сказал(а):</a>
    </div>
    <div class="bbCodeBlock-content">
        <div class="bbCodeBlock-expandContent js-expandContent">
            <!-- ПОЛНЫЙ ТЕКСТ ЦИТАТЫ -->
        </div>
        <div class="bbCodeBlock-expandLink js-expandLink"><a>Нажмите для раскрытия...</a></div>
    </div>
</blockquote>
```

**Правила для ИИ-агента**:
1. **Отделяй слова автора поста от текста цитаты**:
   * Всё, что находится внутри `blockquote.bbCodeBlock--quote` — это чужие слова (автор указан в атрибуте `data-quote`, а ID цитируемого поста — в `data-source="post: <ID>"`).
   * Слова самого автора текущего поста находятся снаружи `blockquote`. Никогда не приписывай текст из цитаты автору ответа!
2. **Раскрывай длинные цитаты в браузере**:
   * Если работаешь визуально в браузере, кликни по `.bbCodeBlock-expandLink a` (или выполни `document.querySelectorAll('.bbCodeBlock-expandLink a').forEach(el => el.click())`).

---

### 4.3. Блоки кода (`[CODE]` / `.bbCodeBlock--code`)
В закрепленных темах («Форма подачи искового заявления», «Шаблон отчета») готовый шаблон часто помещают в блок `<div class="bbCodeBlock bbCodeBlock--screenLimited bbCodeBlock--code">`:
* Внутри лежит тег `<pre><code>...</code></pre>`.
* Именно отсюда нужно копировать сырой BB-код или текст формы, если требуется заполнить заявление строго по образцу.

---

### 4.4. Таблицы (`.bbTable` / `table`)
В реестрах, законах, таблицах штрафов и расписаниях используются таблицы:
* Селектор: `div.bbTable table`
* Читай их построчно (`tr` → ячейки `th` / `td`), сохраняя соответствие колонок. Если внутри ячейки таблицы есть ссылка `<a href="...">`, обязательно извлекай ее `href` вместе с текстом ячейки.

---

## 5. Быстрый однострочник (JS Snippet) для браузерного агента

Если ты используешь браузерный инструмент с возможностью выполнения JavaScript на странице (`evaluate`), выполни этот код сразу после открытия темы, чтобы **мгновенно раскрыть все спойлеры и все свернутые цитаты** на странице:

```javascript
(() => {
  // Раскрываем все спойлеры (включая вложенные)
  document.querySelectorAll('.bbCodeSpoiler-content').forEach(el => {
    el.style.display = 'block';
    el.style.opacity = '1';
    el.classList.add('is-active');
  });
  // Раскрываем все свернутые цитаты и блоки кода
  document.querySelectorAll('.bbCodeBlock--expandable').forEach(el => {
    el.classList.remove('is-expandable');
    el.classList.add('is-expanded');
  });
  return {
    spoilersOpened: document.querySelectorAll('.bbCodeSpoiler-content').length,
    quotesExpanded: document.querySelectorAll('.bbCodeBlock--expandable').length
  };
})();
```
