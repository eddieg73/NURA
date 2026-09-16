# CarePilot FastAPI — propose-only engine (synthetic in-tree store)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Backend sources mounted or copied at build
COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# No secrets required for /health + synthetic store smoke
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
