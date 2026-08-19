#!/usr/bin/env python3
"""ELM327 emulator — sim-first test harness for the OBD2 lane (2026-08-02).
Serves a PTY serial port that answers AT commands + PID queries like a real
ELM327/STN dongle. Verifies python-obd plumbing WITHOUT hardware.
"""
import os, pty, time, threading, sys

PID_TABLE = {
    "0100": "4100BE3EA813",   # PID support
    "0105": "410505A",        # coolant 90C
    "010C": "410C0FA0",       # RPM 1000 (0xFA0/4)
    "010D": "410D003C",       # speed 60 km/h
    "010F": "410F40",         # intake temp 64C
    "0110": "411000",         # MAF
    "012F": "412F32",         # fuel level 50%
    "0142": "414208A",        # battery 13.8V
    "0146": "41461E",         # ambient 30C
}


def elm_respond(line: str) -> str | None:
    cmd = line.strip().upper().replace(" ", "")
    if not cmd:
        return None
    if cmd == "ATZ":
        return "ELM327 v1.5"
    if cmd.startswith("AT"):
        return "OK"
    if cmd == "03" or cmd == "0300":
        return "43 00"  # no DTCs
    if cmd in PID_TABLE:
        return PID_TABLE[cmd]
    if cmd.startswith("01"):
        return "7F 01 12"  # NAK unsupported
    if cmd.startswith("02") or cmd.startswith("04"):
        return "7F 01 12"
    return "?" if cmd.startswith("AT") else "7F 01 12"


def main():
    master, slave = pty.openpty()
    print(f"EMULATOR_READY {os.ttyname(slave)}", flush=True)
    buf = b""
    while True:
        try:
            data = os.read(master, 256)
        except OSError:
            break
        if not data:
            break
        buf += data
        with open("/tmp/elm-traffic.log", "a") as f:
            f.write("RX: " + repr(data) + "\n")
        while b"\r" in buf:
            line, buf = buf.split(b"\r", 1)
            resp = elm_respond(line.decode(errors="ignore"))
            if resp is not None:
                os.write(master, (resp + "\r\r>").encode())  # ELM framing: resp CR CR prompt
    os.close(master)
    os.close(slave)


if __name__ == "__main__":
    main()
