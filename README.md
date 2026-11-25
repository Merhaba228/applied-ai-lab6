# Лабораторная работа №6

Куликов Максим, группа 202М.

[![Docker API check](https://github.com/Merhaba228/applied-ai-lab6/actions/workflows/docker.yml/badge.svg)](https://github.com/Merhaba228/applied-ai-lab6/actions/workflows/docker.yml)

Сделали API для модели из [ЛР4](https://github.com/Merhaba228/applied-ai-lab4). По данным на момент посадки она предсказывает, продлится ли поездка дольше часа. Обученная модель уже лежит в папке `model` и загружается при старте сервиса.

## Как запустить

Нужны Git и запущенный Docker с поддержкой Linux-контейнеров.

```bash
git clone https://github.com/Merhaba228/applied-ai-lab6.git
cd applied-ai-lab6
docker build -t taxi-api .
docker run --rm -p 127.0.0.1:8000:8000 taxi-api
```

Откройте [Swagger UI](http://127.0.0.1:8000/docs), выберите `POST /predict`, затем **Try it out** и **Execute**. Пример можно отправить сразу или изменить значения. Установка Python и скачивание датасета для этого запуска не нужны.

## Как работает запрос

На вход передаём шесть признаков из ЛР4. Час в JSON задаётся числом от 0 до 23, а день недели от 0 до 6, где 0 означает понедельник.

```json
{
  "vendor_id": 1,
  "passenger_count": 2,
  "pickup_longitude": -74.0064,
  "pickup_latitude": 40.7337,
  "pickup_hour": 20,
  "pickup_weekday": 5
}
```

Pydantic проверяет типы и диапазоны до вызова модели. Например, час `24` или строка `"2"` вместо числа пассажиров дают ошибку HTTP 422, в ответе указано проблемное поле. Для правильного запроса модель вернула HTTP 200 и такой ответ:

```json
{
  "predicted_class": 0,
  "long_trip_probability": 0.005804552756035258
}
```

Класс 0 означает поездку до часа включительно, класс 1 означает поездку дольше часа. Второе поле показывает оценку модели для класса 1. Через `GET /health` можно проверить, что сервис запущен и модель загрузилась.

## Проверка

GitHub Actions собирает образ, запускает контейнер и проверяет Swagger, ответ модели и ошибки валидации. Журнал доступен во вкладке [Actions](https://github.com/Merhaba228/applied-ai-lab6/actions/workflows/docker.yml).

Ту же проверку можно запустить в другом терминале, пока контейнер работает:

```bash
python scripts/check_api.py
```

Образ собирается по [примеру из документации FastAPI](https://fastapi.tiangolo.com/deployment/docker/).
