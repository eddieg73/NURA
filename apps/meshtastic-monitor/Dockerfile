# The Meshtastic Monitor — the Linux/Docker deployment (the USB-passthrough works on Linux!)
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0-dev libudev-dev build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY listener.py init_db.py app.py ./
COPY templates/ ./templates/
COPY static/ ./static/

ENV MESHTASTIC_DB=/data/meshtastic.db
ENV MESHTASTIC_DEVICE=/dev/ttyUSB0
ENV PORT=5000

RUN python init_db.py

EXPOSE 5000
CMD ["python", "app.py"]
