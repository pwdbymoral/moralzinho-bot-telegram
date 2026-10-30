FROM python:3.12-slim

WORKDIR /app
COPY bot.py .

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD ["python", "bot.py", "--healthcheck"]

CMD ["python", "-u", "bot.py"]
