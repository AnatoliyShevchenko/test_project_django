FROM python:3.10.12-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind 0.0.0.0:8000", "settings.wsgi"]