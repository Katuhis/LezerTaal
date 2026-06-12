# LezerTaal — план проекта

Языковое приложение для изучения нидерландского (и английского/русского) через чтение.
Загрузка текста → выделение слова → AI-объяснение → сохранение в словарь.

Стек: Python/FastAPI, MongoDB Atlas (`AsyncMongoClient`, pymongo 4.17), pytest-asyncio,
httpx, mongomock-motor, spaCy, Anthropic API. Фронт: SolidJS (муж).

---

## Фаза 1 — Core ✅ закрыта

- [x] Проект, FastAPI-приложение, конфиг и `.env`, GitHub
- [x] MongoDB Atlas, `AsyncMongoClient` (pymongo 4.17), async везде
- [x] Сервис AI-объяснений (`services/ai.py`, `services/prompts.py`)
- [x] CRUD texts и sections (сервисы + роутеры), без хвостовых слешей
- [x] Модели, сериализаторы, `SectionNotEmptyError`
- [x] `db_get_texts` с опциональным `section_id` (секция / корзина), `GET /texts?section_id=`
- [x] `db_delete_texts_by_section`, `DELETE /texts/by-section/{section_id}`
- [x] Все тесты (DB + API, texts + sections) на `mongomock-motor`, 100%

---

## Фаза 2 — Авторизация

- [ ] JWT-авторизация
- [ ] `user_id` из токена вместо хардкода `USER_ID` — заменить в `routers/texts.py` и `routers/sections.py`
- [ ] Регистрация/логин эндпоинты, коллекция `users`
- [ ] Тесты на авторизацию

---

## Фаза 3 — Словарь

- [ ] Endpoint объяснения слова (`word`, `context_sentence`, `text_language`, `user_language` → Claude API, near-zero temperature)
- [ ] Лемматизация через spaCy (`nl_core_news_sm`, `en_core_web_sm`, `ru_core_news_sm`)
- [ ] Кэширование объяснений: ключ = лемма + язык, вызов Claude API только при промахе кэша
- [ ] Карточки в стиле Van Dale NT2: `headword`, `grammar`, `translation`, `example`, `example_translation`
- [ ] Словарь слов и отдельно словарь выражений
- [ ] Сохранение слов в словарь, теги на словах

---

## Фаза 4 — OCR

- [ ] Фото → извлечение текста (image-to-text)

---

## Фаза 5 — Полировка

- [ ] Тренировки по словарю
- [ ] Готовые тексты для чтения (возможно генерация через AI)
- [ ] Async-ревью перед деплоем
- [ ] README для мужа / фронтенд-хендофф

---

## Принципы работы

- Одна задача за раз, конкретная, завершаемая за 1-2 часа
- Код только по явному запросу
- Не давать рекомендации без запроса, не торопить
- Не дни — фазы и задачи