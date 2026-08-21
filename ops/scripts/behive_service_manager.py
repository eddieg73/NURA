#!/usr/bin/env python3
"""Bounded lifecycle manager for local BeHive and its PostgreSQL backend."""

from __future__ import annotations

import argparse
import json
import os
import pwd
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path('/opt/data/behive-runtime')
PG_PREFIX = Path('/opt/data/postgresql-16.14')
PG_BIN = PG_PREFIX / 'bin'
PG_DATA = ROOT / 'postgres-primary'
PG_LOG = ROOT / 'postgres-primary.log'
PG_PORT = 5434
PG_USER = pwd.getpwuid(os.getuid()).pw_name
DB_NAME = 'behive'
DB_URL = f'postgresql://127.0.0.1:{PG_PORT}/{DB_NAME}'

BEHIVE_HOME = Path('/opt/data/home/behive')
BEHIVE_BIN = BEHIVE_HOME / '.venv' / 'bin' / 'behive'
BEHIVE_PID = ROOT / 'behive.pid'
BEHIVE_LOG = ROOT / 'behive.log'
BEHIVE_SCHEMA = BEHIVE_HOME / 'docker' / 'init-db.sql'
HERMES_ENV = Path('/opt/data/.env')
API_URL = 'http://127.0.0.1:8091'
MCP_URL = 'http://127.0.0.1:8090/mcp'


def read_env_value(name: str) -> str | None:
    if not HERMES_ENV.is_file():
        return None
    for raw in HERMES_ENV.read_text(encoding='utf-8', errors='replace').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key.strip() != name:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        return value or None
    return None


def socket_open(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=timeout):
            return True
    except OSError:
        return False


def run_checked(command: list[str], *, timeout: int = 60, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=capture,
        check=True,
        timeout=timeout,
        env={
            **{key: value for key, value in os.environ.items() if key in {
                'HOME', 'USER', 'LANG', 'LC_ALL', 'TERM', 'TMPDIR', 'XDG_RUNTIME_DIR'
            }},
            'PATH': f'{PG_BIN}:/usr/local/bin:/usr/bin:/bin',
        },
    )


def psql(database: str, sql: str, *, tuples_only: bool = True) -> str:
    command = [
        str(PG_BIN / 'psql'),
        '--no-password',
        '--host', '127.0.0.1',
        '--port', str(PG_PORT),
        '--username', PG_USER,
        '--dbname', database,
        '--set', 'ON_ERROR_STOP=1',
    ]
    if tuples_only:
        command.extend(['--tuples-only', '--no-align'])
    command.extend(['--command', sql])
    return run_checked(command, timeout=30).stdout.strip()


def postgres_healthy() -> bool:
    if not socket_open(PG_PORT):
        return False
    try:
        return psql('postgres', 'SELECT 1;') == '1'
    except Exception:
        return False


def prepare() -> None:
    required = [
        PG_BIN / 'postgres', PG_BIN / 'initdb', PG_BIN / 'pg_ctl',
        PG_BIN / 'psql', PG_BIN / 'createdb', BEHIVE_BIN, BEHIVE_SCHEMA,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError('Required BeHive runtime files are unavailable: ' + ', '.join(missing))
    for path in (ROOT, PG_DATA):
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)


def initialize_postgres() -> None:
    if (PG_DATA / 'PG_VERSION').is_file():
        return
    run_checked([
        str(PG_BIN / 'initdb'),
        '--pgdata', str(PG_DATA),
        '--encoding', 'UTF8',
        '--locale', 'C',
        '--auth-local', 'trust',
        '--auth-host', 'trust',
    ], timeout=120)
    config = PG_DATA / 'postgresql.conf'
    marker = '# BeHive local runtime settings\n'
    settings = (
        f"\n{marker}"
        "listen_addresses = '127.0.0.1'\n"
        f"port = {PG_PORT}\n"
        f"unix_socket_directories = '{ROOT}'\n"
        "max_connections = 50\n"
    )
    content = config.read_text(encoding='utf-8')
    if marker not in content:
        config.write_text(content + settings, encoding='utf-8')
    config.chmod(0o600)


def start_postgres() -> None:
    if postgres_healthy():
        return

    pid_file = PG_DATA / 'postmaster.pid'
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(encoding='utf-8').splitlines()[0])
            cmdline = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except Exception:
            pid = None
            cmdline = ''
        if pid and str(PG_DATA) in cmdline and str(PG_BIN / 'postgres') in cmdline:
            raise RuntimeError(f'PostgreSQL PID {pid} is alive but readiness failed')
        pid_file.unlink(missing_ok=True)

    log = PG_LOG.open('ab', buffering=0)
    process = subprocess.Popen(
        [
            str(PG_BIN / 'postgres'), '-D', str(PG_DATA),
            '-h', '127.0.0.1', '-p', str(PG_PORT),
        ],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
        env={
            **{key: value for key, value in os.environ.items() if key in {
                'HOME', 'USER', 'LANG', 'LC_ALL', 'TERM', 'TMPDIR', 'XDG_RUNTIME_DIR'
            }},
            'PATH': f'{PG_BIN}:/usr/local/bin:/usr/bin:/bin',
        },
    )
    log.close()
    for _ in range(60):
        if postgres_healthy():
            return
        if process.poll() is not None:
            break
        time.sleep(0.5)
    raise RuntimeError(f'PostgreSQL failed readiness; inspect {PG_LOG}')


def ensure_schema() -> None:
    exists = psql('postgres', f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
    if exists != '1':
        run_checked([
            str(PG_BIN / 'createdb'),
            '--host', '127.0.0.1',
            '--port', str(PG_PORT),
            '--username', PG_USER,
            DB_NAME,
        ], timeout=30)
    run_checked([
        str(PG_BIN / 'psql'),
        '--no-password',
        '--host', '127.0.0.1',
        '--port', str(PG_PORT),
        '--username', PG_USER,
        '--dbname', DB_NAME,
        '--set', 'ON_ERROR_STOP=1',
        '--file', str(BEHIVE_SCHEMA),
    ], timeout=60)


def api_health(timeout: float = 2.0) -> tuple[bool, dict]:
    try:
        with urllib.request.urlopen(f'{API_URL}/health', timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
        return response.status == 200 and data.get('status') == 'ok', data
    except Exception as exc:
        return False, {'error': f'{type(exc).__name__}: {exc}'}


def mcp_request(method: str, params: dict | None = None, timeout: float = 3.0) -> dict:
    payload: dict = {'jsonrpc': '2.0', 'id': 1, 'method': method}
    if params is not None:
        payload['params'] = params
    request = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
        },
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def mcp_health() -> tuple[bool, list[str]]:
    try:
        initialized = mcp_request('initialize')
        listed = mcp_request('tools/list')
        server_name = initialized.get('result', {}).get('serverInfo', {}).get('name')
        names = [tool.get('name', '') for tool in listed.get('result', {}).get('tools', [])]
        expected = {'research_topic', 'search_knowledge', 'get_report', 'mission_status'}
        return server_name == 'behive' and expected.issubset(set(names)), names
    except Exception:
        return False, []


def read_pid() -> int | None:
    try:
        return int(BEHIVE_PID.read_text(encoding='utf-8').strip())
    except Exception:
        return None


def process_matches(pid: int) -> bool:
    try:
        cmdline = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except Exception:
        return False
    return str(BEHIVE_BIN) in cmdline and ' serve ' in f' {cmdline} '


def active_behive_pid() -> int | None:
    """Return the live BeHive parent PID and repair a stale PID file."""
    recorded = read_pid()
    if recorded and process_matches(recorded):
        return recorded

    candidates: list[tuple[bool, int]] = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        pid = int(proc.name)
        if not process_matches(pid):
            continue
        try:
            ppid = int((proc / 'stat').read_text(encoding='utf-8').split()[3])
        except Exception:
            ppid = -1
        candidates.append((ppid != 1, pid))

    if not candidates:
        BEHIVE_PID.unlink(missing_ok=True)
        return None

    _, pid = min(candidates)
    BEHIVE_PID.write_text(f'{pid}\n', encoding='utf-8')
    BEHIVE_PID.chmod(0o600)
    return pid


def behive_environment() -> dict[str, str]:
    openai_key = read_env_value('OPENAI_API_KEY')
    if not openai_key:
        raise RuntimeError(f'OPENAI_API_KEY is not configured in {HERMES_ENV}')
    base = {
        key: value for key, value in os.environ.items()
        if key in {'HOME', 'USER', 'LANG', 'LC_ALL', 'TERM', 'TMPDIR', 'XDG_RUNTIME_DIR'}
    }
    base.update({
        'PATH': f'{BEHIVE_HOME / ".venv" / "bin"}:{PG_BIN}:/usr/local/bin:/usr/bin:/bin',
        'PYTHONPATH': '',
        'DATABASE_URL': DB_URL,
        'BEHIVE_DB_URL': DB_URL,
        'BEHIVE_API_PORT': '8091',
        'BEHIVE_LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': openai_key,
    })
    return base


def stop_behive(quiet: bool = False) -> None:
    pid = active_behive_pid()
    if not pid:
        return
    os.killpg(pid, signal.SIGTERM)
    for _ in range(60):
        if not Path(f'/proc/{pid}').exists():
            BEHIVE_PID.unlink(missing_ok=True)
            if not quiet:
                print(f'BeHive stopped pid={pid}')
            return
        time.sleep(0.25)
    raise RuntimeError(f'BeHive PID {pid} did not stop cleanly')


def start_behive() -> int:
    pid = active_behive_pid()
    api_ok, _ = api_health()
    mcp_ok, _ = mcp_health()
    if api_ok and mcp_ok:
        return pid or 0

    if pid:
        stop_behive(quiet=True)
    else:
        BEHIVE_PID.unlink(missing_ok=True)

    log = BEHIVE_LOG.open('ab', buffering=0)
    process = subprocess.Popen(
        [
            str(BEHIVE_BIN), 'serve', '--host', '127.0.0.1',
            '--port', '8091', '--mcp-port', '8090',
        ],
        cwd=str(BEHIVE_HOME),
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
        env=behive_environment(),
    )
    log.close()
    BEHIVE_PID.write_text(f'{process.pid}\n', encoding='utf-8')
    BEHIVE_PID.chmod(0o600)

    for _ in range(80):
        api_ok, _ = api_health(timeout=0.75)
        mcp_ok, _ = mcp_health()
        if api_ok and mcp_ok:
            return process.pid
        if process.poll() is not None:
            break
        time.sleep(0.5)
    raise RuntimeError(f'BeHive failed readiness; inspect {BEHIVE_LOG}')


def start(quiet: bool = False) -> int:
    prepare()
    initialize_postgres()
    start_postgres()
    ensure_schema()
    pid = start_behive()
    if not quiet:
        print(f'BeHive started pid={pid} api={API_URL} mcp={MCP_URL} database=127.0.0.1:{PG_PORT}/{DB_NAME}')
    return 0


def stop(quiet: bool = False) -> int:
    stop_behive(quiet=quiet)
    if postgres_healthy():
        run_checked([
            str(PG_BIN / 'pg_ctl'), '--pgdata', str(PG_DATA),
            '--wait', '--timeout', '30', 'stop', '--mode', 'fast',
        ], timeout=45)
        if not quiet:
            print('BeHive PostgreSQL stopped')
    return 0


def status() -> int:
    pg_ok = postgres_healthy()
    api_ok, api_data = api_health()
    mcp_ok, tools = mcp_health()
    pid = active_behive_pid()
    print(f'postgres_healthy={str(pg_ok).lower()}')
    print(f'api_healthy={str(api_ok).lower()}')
    print(f'mcp_healthy={str(mcp_ok).lower()}')
    print(f'pid={pid or ""}')
    print(f'pid_matches={str(bool(pid and process_matches(pid))).lower()}')
    print(f'api_status={api_data.get("status", "unavailable")}')
    print(f'mcp_tools={len(tools)}')
    print(f'api_url={API_URL}')
    print(f'mcp_url={MCP_URL}')
    return 0 if pg_ok and api_ok and mcp_ok else 1


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
        stop(quiet=True)
        return start(args.quiet)
    return status()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'behive-manager error: {exc}', file=sys.stderr)
        raise SystemExit(1)
