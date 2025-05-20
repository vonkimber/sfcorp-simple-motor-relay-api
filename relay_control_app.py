from flask import Flask, render_template_string, jsonify
import serial, time, os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configurable serial settings via environment or defaults
SERIAL_PORT = os.getenv('RELAY_SERIAL_PORT', 'COM3')
BAUD_RATE = int(os.getenv('RELAY_BAUD', '9600'))
TIMEOUT_S = float(os.getenv('RELAY_TIMEOUT', '1'))  # in seconds for ON commands

# Serial helper
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    raise RuntimeError(f"Could not open serial port {SERIAL_PORT}: {e}")

 def send_frame(relays):
    """
    Send an 8-byte command to specified relay(s).

    relays: list of tuples (relay_num, state_bool)
    """
    for num, on in relays:
        state = 0x01 if on else 0x02
        frame = [0x55, 0x56, 0x00, 0x00, 0x00, num, state]
        checksum = sum(frame) & 0xFF
        frame.append(checksum)
        ser.write(bytes(frame))
        time.sleep(0.2)

# Flask app
app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<title>Relay Control</title>
<h1>Relay Control Panel</h1>
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
    # Ensure relay2 is OFF, then relay1 ON for TIMEOUT_S seconds
    send_frame([(2, False), (1, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(1, False)])
    return jsonify(status=f'UP executed with {TIMEOUT_S}s timeout')

@app.route('/down')
def down():
    # Relay1 OFF, Relay2 ON for TIMEOUT_S seconds
    send_frame([(1, False), (2, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(2, False)])
    return jsonify(status=f'DOWN executed with {TIMEOUT_S}s timeout')

@app.route('/stop')
def stop():
    # Both ON for TIMEOUT_S seconds
    send_frame([(1, True), (2, True)])
    time.sleep(TIMEOUT_S)
    send_frame([(1, False), (2, False)])
    return jsonify(status=f'STOP executed with {TIMEOUT_S}s timeout')

@app.route('/off')
def off():
    # Both OFF immediately
    send_frame([(1, False), (2, False)])
    return jsonify(status='OFF executed')

if __name__ == '__main__':
    # Run Flask on default port 5000, config via env FLASK_RUN_HOST, FLASK_RUN_PORT
    app.run(host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_RUN_PORT', 5000)))
