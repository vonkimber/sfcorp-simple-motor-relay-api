#!/usr/bin/env python3
"""
screen_control_app.py: Flask web server to control a 2-channel RS-232 relay board.
Reads configuration from environment or .env and exposes UP, DOWN, STOP, OFF endpoints.
"""
import os
import time
import serial
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configuration defaults
SERIAL_PORT = os.getenv('RELAY_SERIAL_PORT', 'COM3')
BAUD_RATE = int(os.getenv('RELAY_BAUD', '9600'))
TIMEOUT_S = float(os.getenv('RELAY_TIMEOUT', '1'))
HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_RUN_PORT', '5000'))

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    raise RuntimeError(f"Could not open serial port {SERIAL_PORT}: {e}")

# Helper to send frames
def send_frame(relays):
    """
    Send an 8-byte command for each (relay_num, state_bool) in relays.
    state_bool: True for ON (0x01), False for OFF (0x02)
    """
    for num, on in relays:
        state_byte = 0x01 if on else 0x02
        frame = [0x55, 0x56, 0x00, 0x00, 0x00, num, state_byte]
        checksum = sum(frame) & 0xFF
        frame.append(checksum)
        ser.write(bytes(frame))
        time.sleep(0.2)

# Create Flask app
app = Flask(__name__)
TEMPLATE = '''
<!doctype html>
<title>Relay Control</title>
<h1>Screen Control Panel</h1>
<button onclick="fetch('/up').then(r=>r.json()).then(j=>status.textContent=j.status)">UP</button>
<button onclick="fetch('/down').then(r=>r.json()).then(j=>status.textContent=j.status)">DOWN</button>
<button onclick="fetch('/stop').then(r=>r.json()).then(j=>status.textContent=j.status)">STOP</button>
<button onclick="fetch('/off').then(r=>r.json()).then(j=>status.textContent=j.status)">OFF</button>
<p id="status"></p>
'''

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/up')
def up():
    # Relay2 OFF, Relay1 ON for TIMEOUT_S seconds
    send_frame([(2, False), (1, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(1, False)])
    return jsonify(status=f'UP executed ({TIMEOUT_S}s)')

@app.route('/down')
def down():
    # Relay1 OFF, Relay2 ON for TIMEOUT_S seconds
    send_frame([(1, False), (2, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(2, False)])
    return jsonify(status=f'DOWN executed ({TIMEOUT_S}s)')

@app.route('/stop')
def stop():
    # Both ON for TIMEOUT_S seconds
    send_frame([(1, True), (2, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(1, False), (2, False)])
    return jsonify(status=f'STOP executed ({TIMEOUT_S}s)')

@app.route('/off')
def off():
    # Both OFF immediately
    send_frame([(1, False), (2, False)])
    return jsonify(status='OFF executed')


def main():
    app.run(host=HOST, port=PORT)

if __name__ == '__main__':
    main()
