# The Meshtastic Node Monitor — the deployment guide!

## The architecture
- **listener.py** — the USB radio-interface (the Heltec V4!) → the onReceive-callbacks → the SQLite-DB!
- **app.py** — the Flask API (the /api/health · /api/stats · /api/packets · /api/nodes · /api/export.csv!)
- **templates/index.html + static/** — the custom-JS/CSS frontend (the live-map · the tables · the CSV-downloads!)
- **db.py** (init_db helper!) — the schema + the maintenance!

## The deployment (the TARGET-SPECIFIC!)

### Option A — macOS native (the Mac's Docker can't pass the USB!)
```bash
# 1. find the USB port (before/after plugging the radio!)
ls /dev/cu.*
#    → the new device: /dev/cu.usbmodem14101 or /dev/cu.SLAB_USBtoUART

# 2. the venv
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. the DB-init
python init_db.py

# 4. TWO TERMINAL TABS (the listener + the web!)
# Tab 1:
source venv/bin/activate && python listener.py
# Tab 2:
source venv/bin/activate && python app.py

# 5. the dashboard!
#    local:  http://localhost:5000
#    LAN:    http://<your-mac-ip>:5000 (System Settings → Network!)
```

### Option B — the Raspberry Pi 5 (the native, the same as Mac!)
```bash
ls /dev/ttyUSB*        # the radio-port!
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python init_db.py
# the two-tabs (or systemd-units for the auto-start!)
python listener.py  &   # tab 1
python app.py       &   # tab 2
```

### Option C — Linux/Docker (the USB-passthrough WORKS on Linux!)
```bash
docker compose up -d --build
# the compose maps the /dev/ttyUSB0 into the container!
```

## The environment variables
- `MESHTASTIC_DEVICE` — the serial-port (default /dev/ttyUSB0; Mac: /dev/cu.usbmodemXXXX!)
- `MESHTASTIC_DB` — the SQLite-path (default /data/meshtastic.db!)
- `PORT` — the Flask-port (default 5000!)

## The DB-maintenance
- The auto-vacuum + the old-packet-pruning (see db.py — run `python init_db.py --prune-days 30` weekly via cron!)
- The backup: `cp meshtastic.db meshtastic-$(date +%F).db`!
