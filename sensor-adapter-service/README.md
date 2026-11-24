# Sensor Adapter Service

Принимает бинарные пакеты с трекеров, проверяет CRC-8 каждого сообщения и сохраняет сообщения типа `0x02` в PostgreSQL.

Формат пакета описан в [binary-protocol.md](https://github.com/AlexixRugis/birdtracker/blob/main/docs/protocol/binary-protocol.md) в репозитории прошивки.

## Приём пакетов

| Канал | Куда отправлять | Ответ |
|-------|-----------------|-------|
| HTTP | `POST /api/v1/sensors/binary`, пакет в теле запроса | `{"device_id": "...", "saved_messages": 1}` |
| TCP | порт 9999, один пакет на соединение | `OK <n>` или `ERR <причина>` |
| UDP | порт 9998, один пакет в датаграмме | `OK <n>` или `ERR <причина>` |

`n` — число сохранённых сообщений. TCP и UDP включаются переменными `ENABLE_TCP_SERVER` и `ENABLE_UDP_SERVER`.

```bash
curl -X POST \
     -H "Content-Type: application/octet-stream" \
     --data-binary @packet.bin \
     http://localhost:8002/api/v1/sensors/binary
```

## Чтение данных

`GET /api/v1/sensors/data?internal_id=<device_id>` возвращает координаты устройства.
Необязательные параметры: `date_from`, `date_to`, `limit`, `order` (`asc` или `desc`).

## Настройка и запуск

Переменные окружения перечислены в `.env_example`. Запуск, тесты и миграции описаны в [README в корне](../README.md).
