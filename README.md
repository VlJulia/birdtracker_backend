# Bird Tracking Service

Бэкенд проекта Birdtracker: принимает данные с трекеров на птицах и отдаёт их через API.

## Из чего состоит

| Сервис | Папка | Что делает | Порты |
|--------|-------|------------|-------|
| API | `backend/` | птицы, сенсоры, расчёты по трекам | 8000 |
| Адаптер | `sensor-adapter-service/` | принимает пакеты с трекеров по HTTP, TCP и UDP | 8002, 9999, 9998/udp |

У каждого сервиса своя база PostgreSQL. Треки API запрашивает у адаптера по HTTP.

## Запуск

Нужен Docker.

```bash
docker network create shared-net    # один раз
cp infra/.env_example infra/.env
cp sensor-adapter-service/.env_example sensor-adapter-service/.env

docker compose -f infra/docker-compose.yaml up --build -d
docker compose -f sensor-adapter-service/docker-compose.yml up --build -d
```

Эндпоинты описаны в Swagger: <http://localhost:8000/docs> (API) и <http://localhost:8002/docs> (адаптер).

## Разработка

Нужен [uv](https://docs.astral.sh/uv/). Команды выполняются в папке сервиса.

```bash
uv sync           # установить зависимости
uv run pytest     # тесты
uv add <пакет>    # добавить зависимость
```

Код форматирует и проверяет ruff. Чтобы он запускался сам при каждом коммите:

```bash
uvx pre-commit install
```

Те же проверки и тесты идут в CI на каждый pull request.

## Миграции

Схему базы меняет только Alembic. При старте контейнера миграции применяются сами.

После изменения моделей создайте миграцию, примените и закоммитьте её:

```bash
docker compose -f infra/docker-compose.yaml exec web alembic revision --autogenerate -m "что изменилось"
docker compose -f infra/docker-compose.yaml exec web alembic upgrade head
```

Для адаптера команды те же, но с `-f sensor-adapter-service/docker-compose.yml exec sensor-adapter`.

## Лицензия

MIT, см. [LICENSE](LICENSE).
