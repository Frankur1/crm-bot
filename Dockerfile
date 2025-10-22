# Используем официальный Python
FROM python:3.13-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем переменные окружения
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "crm_questions_bot.py"]
