import sys
import socket
import time
import logging
import oracledb
from scripts.utils.config import load_config, get_dsn, get_db_user

log = logging.getLogger(__name__)

def wait_for_oracle(password):
    cfg = load_config()
    db = cfg["database"]
    wait = cfg["wait"]
    host = db["host"]
    port = db["port"]
    dsn = get_dsn(cfg)
    user = get_db_user(cfg)
    max_attempts = wait["max_attempts"]
    sleep_interval = wait["sleep_interval"]

    for i in range(max_attempts):
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
        except OSError:
            time.sleep(sleep_interval)
            continue

        try:
            c = oracledb.connect(user=user, password=password, dsn=dsn)
            c.close()
            log.info(f"Oracle ready after {(i + 1) * sleep_interval}s")
            sys.exit(0)
        except Exception as e:
            log.warning(f"attempt {i + 1}: {e}")

        time.sleep(sleep_interval)

    log.error(f"Failed after {max_attempts * sleep_interval}s")
    sys.exit(1)
