# Screen Control App

A lightweight Flask-based web application to control a 2‑channel RS‑232 relay board (e.g. a motorized screen). Provides a simple REST UI with **UP**, **DOWN**, **STOP**, and **OFF** buttons—and a corresponding CLI utility for scripted control.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Web App](#running-the-web-app)
5. [Using the CLI Utility](#using-the-cli-utility)
6. [Running in Docker](#running-in-docker)
7. [File Structure](#file-structure)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

* **Python 3.7+** installed and added to your `PATH` (Windows/macOS/Linux)
* **pip** for installing Python packages
* A **2‑channel RS‑232 relay board** connected to your PC (via FTDI or similar adapter)

---

## Installation

1. **Clone or download** this repository:

   ```bash
   git clone https://github.com/your-org/screen-control-app.git
   cd screen-control-app
   ```
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   # or install as a package
   pip install .
   ```
3. Ensure the **CLI entry point** is available:

   ```bash
   relay-web --help
   ```

---

## Configuration

All settings are driven by environment variables (or a `.env` file in the project root). Create a file named `.env` with:

```ini
RELAY_SERIAL_PORT=COM3        # Windows COM port, or /dev/ttyUSB0 on Linux
RELAY_BAUD=9600              # Baud rate (default: 9600)
RELAY_TIMEOUT=1              # Seconds to hold ON commands
FLASK_RUN_HOST=0.0.0.0       # Host for Flask (0.0.0.0 to expose)
FLASK_RUN_PORT=5000          # Port for Flask web server
```

> **Tip:** On Linux, map COMx to `/dev/ttyS<n-1>` or use your adapter’s `/dev/ttyUSB*` device.

---

## Running the Web App

### Native Python

```bash
# Start the web server
relay-web
```

Then open your browser to [http://localhost:5000](http://localhost:5000) (or `http://<your-ip>:5000` on your network).

---

## Using the CLI Utility

A companion script (`relay_cli.py`) lets you fire individual relay commands from the shell:

```bash
# Turn Relay 1 ON
python relay_cli.py 1 on

# Turn Relay 2 OFF on a different port
python relay_cli.py --port /dev/ttyUSB0 2 off

# Turn both relays ON
python relay_cli.py both on
```

---

## Running in Docker

1. **Build** the Docker image:

   ```bash
   docker build -t screen-control-app .
   ```
2. **Run** with your `.env` file:

   ```bash
   docker run -d \
     --name screen-control \
     --env-file .env \
     -p ${FLASK_RUN_PORT}:5000 \
     screen-control-app
   ```
3. **Access** at `http://localhost:5000` (or mapped host).

---

## File Structure

```
├── screen_control_app.py   # Main Flask application
├── relay_cli.py            # CLI utility for direct control
├── requirements.txt        # Python dependencies
├── setup.py                # Package metadata and entry points
├── Dockerfile              # Docker container definition
└── .env                    # Environment configuration (gitignored)
```

---

## Troubleshooting

* **No serial port found**: Verify `RELAY_SERIAL_PORT` points to a valid device (e.g., `COM3` or `/dev/ttyUSB0`).
* **Permission denied** (Linux): Add your user to the `dialout` group or run with `sudo`.
* **Relay doesn’t click**: Ensure the board is powered (12 V) and ground is shared with your serial adapter.

---
