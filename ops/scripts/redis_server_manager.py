#!/usr/bin/env python3
"""Bounded lifecycle manager for the local Redis server."""

from __future__ import annotations

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/opt/data/redis-server')
BIN = Path('/opt/data/redis/bin/redis-server')
CONFIG = ROOT / 'redis.conf'
PID_FILE = ROOT / 'redis.pid'
LOG_FILE = ROOT / 'redis.log'


def healthy(timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection(('127.0.0.1', 6379), timeout=timeout) as sock:
            sock.sendall(b'*1\r\n$4\r\nPING\r\n')
            return sock.recv(64).startswith(b'+PONG')
    except Exception:
        return False


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding='utf-8').strip())
    except Exception:
        return None


def process_matches(pid: int) -> bool:
    try:
        executable = Path(f'/proc/{pid}/exe').resolve()
    except Exception:
        return False
    return executable == BIN.resolve()


def prepare() -> None:
    if not BIN.exists() or not os.access(BIN, os.X_OK):
        raise RuntimeError(f'Redis binary is unavailable: {BIN}')
    if not CONFIG.is_file():
        raise RuntimeError(f'Redis config is unavailable: {CONFIG}')
    for path in (ROOT, ROOT / 'data'):
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)


def start(quiet: bool = False) -> int:
    prepare()
    if healthy():
        return 0
    pid = read_pid()
    if pid and process_matches(pid):
        for _ in range(20):
            if healthy():
                return 0
            time.sleep(0.5)
        raise RuntimeError(f'Redis PID {pid} is alive but health did not recover')
    PID_FILE.unlink(missing_ok=True)
    log = LOG_FILE.open('ab', buffering=0)
    process = subprocess.Popen(
        [str(BIN), str(CONFIG)],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
        env=os.environ.copy(),
    )
    log.close()
    for _ in range(60):
        if healthy():
            if not quiet:
                print(f'Redis started pid={process.pid} url=redis://127.0.0.1:6379/0')
            return 0
        if process.poll() is not None:
            break
        time.sleep(0.25)
    raise RuntimeError(f'Redis failed readiness; inspect {LOG_FILE}')


def stop(quiet: bool = False) -> int:
    pid = read_pid()
    if not pid or not process_matches(pid):
        PID_FILE.unlink(missing_ok=True)
        return 0
    os.kill(pid, signal.SIGTERM)
    for _ in range(40):
        if not Path(f'/proc/{pid}').exists():
            PID_FILE.unlink(missing_ok=True)
            if not quiet:
                print(f'Redis stopped pid={pid}')
            return 0
        time.sleep(0.25)
    raise RuntimeError(f'Redis PID {pid} did not stop cleanly')


def status() -> int:
    pid = read_pid()
    ok = healthy()
    print(f'healthy={str(ok).lower()}')
    print(f'pid={pid or ""}')
    print(f'pid_matches={str(bool(pid and process_matches(pid))).lower()}')
    print('url=redis://127.0.0.1:6379/0')
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('ensure', 'start', 'stop', 'restart', 'status'))
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    if args.action in {'ensure', 'start'}:
        return start(args.quiet)
    if args.action == 'stop':
        return stop(args.quiet)
    if args.action == 'restart':
        stop(True)
        return start(args.quiet)
    return status()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'redis-manager error: {exc}', file=sys.stderr)
        raise SystemExit(1)
