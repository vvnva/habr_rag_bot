# Habr RAG
## Общее описание
Решение представляет собой систему для анализа и обработки контента с Хабра. Система осуществляет поиск релевантных статей, извлекает данные и предоставляет ответы на вопросы в соответствии с извлеченной информацией и отображает подходящие ссылки с Хабра.
## Данные
Данные взяты из открытого датасета на Hugging Face: [IlyaGusev/habr](https://huggingface.co/datasets/IlyaGusev/habr), содержащий информацию о статьях с платформы Habr. Для анализа было взято **10%** датасета.
- **Общее количество статей**: 30204
- **Разрез данных**: 2006-05-02 — 2023-02-10
- **Количество колонок в датасете**: 22
- **Используемые колонки**:
Для анализа данных были использованы следующие колонки:
  - `url` — ссылка на статью.
  - `title` — заголовок статьи.
  - `text_markdown` — текст статьи в формате Markdown.

  `title` и `text_markdown` — для содержимого документов.
  `url` и `title` — в метаданных для идентификации статей.
- **Количество полученных документов**: 285378

#### 10 самых популярных тегов и пар тегов (биграмм) вместе с их частотой использования:
<div align="center">

| **Тег**         | **Частота** |          |          |          | **Биграмма**          | **Частота** |
|------------------|------------|----------|----------|----------|------------------------|-------------|
| javascript       | 563        |          |          |          | (css, html)            | 81          |
| python           | 486        |          |          |          | (apple, iphone)        | 71          |
| android          | 434        |          |          |          | (css, js)              | 56          |
| google           | 431        |          |          |          | (ios, swift)           | 51          |
| linux            | 411        |          |          |          | (дайджест, новости)    | 49          |
| java             | 374        |          |          |          | (android, ios)         | 48          |
| php              | 368        |          |          |          | (дайджест, ссылки)     | 47          |
| разработка       | 355        |          |          |          | (Apple, iPhone)        | 45          |
| apple            | 352        |          |          |          | (css, дайджест)        | 44          |
| microsoft        | 346        |          |          |          | (android, google)      | 44          |

</div>

## Архитектура решения
### Rag Pipeline
<div align="center">
    <img src="https://drive.google.com/uc?export=view&id=1S_GuFPctPRfCkeFDkhSSw5XKMuWIlfk0" alt="Граф">
</div>

Дополнительно также реализована память в рамках диалога с конкретным пользователем, авторизация в стримлите и сохранение диалогов для пользователя по логину/паролю.
## Валидация
Для расчета метрик было сгенерировано 75 вопросов, ответы на которые наиболее вероятно могут быть на Хабре.
### Retrieved docs vs input
<div align="center">

| **k**  | **Precision (p@k)** |
|--------|----------------------|
| 1      | 0.6133              |
| 2      | 0.7067              |
| 3      | 0.8667              |
| 4      | 0.9200              |
| 5      | 0.9467              |
| 10     | 0.9733              |

**MAP**: 0.6429

</div>

<div align="center">
    <img src="https://drive.google.com/uc?export=view&id=1-9GbsSSpT1JRNmmPsid-CL3Q7N4tv_S-" alt="Precision at k">
</div>

### Generation vs input
**Accuracy**: 0.753

## Структура репозитория
```
 ├── data/ # Данные проекта 
 ├── db/ # Структура и файлы базы данных 
 ├── src/ # Исходный код 
 ├── tests/ # Метрики 
 └── ui/ # Интерфейс пользователя 
 ```

## Запуск

## Примеры интерфейса 

## Состав команды
- [Набиуллин Иван](https://t.me/xenopupel)
- [Артемьев Никита](https://t.me/d_narti)
- [Иванова Вера](https://t.me/v_vnva)
