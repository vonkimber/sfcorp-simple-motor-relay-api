#!/usr/bin/env python3
"""
relay_cli.py: CLI utility to control a 2-channel RS-232 relay board.

Usage:
  relay_cli.py 1 on               # Turn Relay 1 ON on default COM3
  relay_cli.py 2 off              # Turn Relay 2 OFF
  relay_cli.py both on            # Turn both relays ON
  relay_cli.py both off           # Turn both relays OFF
  relay_cli.py -p COM4 1 on       # Use COM4 instead of default COM3
  relay_cli.py --port COM5 2 off  # Use COM5
  relay_cli.py -p COM6 -b 19200 both on  # Override baud rate

Note:
  - On Windows, use the native Python interpreter, not under WSL2.
  - COM ports under WSL2 often cannot be accessed; run this script in PowerShell or CMD.
"""
import argparse
import time
import platform
import serial
import sys


def normalize_port(port: str) -> str:
    """
    Normalize a COMx on Windows to the appropriate device path on Linux under full distros.
    WSL2 does not support serial port access.
    """
    if platform.system() == 'Linux':
        # Detect WSL2
        try:
            with open('/proc/version', 'r') as f:
                if 'Microsoft' in f.read():
                    print("Error: WSL2 cannot access serial ports. Please run under native Windows Python.")
                    sys.exit(1)
        except FileNotFoundError:
            pass
        # map COMx to ttyS<n-1> for full Linux
        if port.upper().startswith('COM'):
            try:
                num = int(port[3:])
                return f"/dev/ttyS{num-1}"
            except ValueError:
                pass
    return port


def set_relay(ser, relay_id, state):
    """
    Send an 8-byte command to set the specified relay or both relays.
    :param ser: open pySerial Serial instance
    :param relay_id: '1', '2', or 'both'
    :param state: 'on' or 'off'
    """
    relays = [int(relay_id)] if relay_id in ['1', '2'] else [1, 2]
    state_byte = 0x01 if state == 'on' else 0x02
    for r in relays:
        frame = [0x55, 0x56, 0x00, 0x00, 0x00, r, state_byte]
        checksum = sum(frame) & 0xFF
        frame.append(checksum)
        ser.write(bytes(frame))
        time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser(
        description='Control a 2-channel RS-232 relay board via a COM port.'
    )
    parser.add_argument(
        'relay', choices=['1', '2', 'both'],
        help='Relay identifier: "1", "2", or "both"'
    )
    parser.add_argument(
        'action', choices=['on', 'off'],
        help='Action to perform on the relay(s)'
    )
    parser.add_argument(
        '-p', '--port', default='COM3',
        help='Serial port (default: COM3)'
    )
    parser.add_argument(
        '-b', '--baudrate', type=int, default=9600,
        help='Baud rate (default: 9600)'
    )
    args = parser.parse_args()

    port_name = normalize_port(args.port)
    try:
        with serial.Serial(
            port=port_name,
            baudrate=args.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        ) as ser:
            set_relay(ser, args.relay, args.action)
    except serial.SerialException as e:
        print(f"Error opening {port_name}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
