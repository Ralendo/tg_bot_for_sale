# Используйте базовый образ Python
FROM python:3.9
LABEL Auther="ralendo"

# Устанавливаем зависимости
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Команда для запуска приложения
CMD ["python", "/app/src/bot.py"]
