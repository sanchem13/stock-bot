FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY line_bot.py .
EXPOSE 8000
CMD ["gunicorn", "line_bot:app", "--bind", "0.0.0.0:8000", "--workers", "1"]
