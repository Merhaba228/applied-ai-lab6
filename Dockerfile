FROM python:3.12-slim-bookworm

WORKDIR /service
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app/main.py app/main.py
COPY model/taxi_model.pkl model/taxi_model.pkl

USER 10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
