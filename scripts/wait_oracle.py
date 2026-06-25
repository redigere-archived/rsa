import sys
import socket
import time
import logging
import oracledb

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def wait_for_oracle(password):
    host = "localhost"
    port = 1521
    service = "FREEPDB1"

    for i in range(120):
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
        except OSError:
            time.sleep(5)
            continue

        try:
            c = oracledb.connect(user="system", password=password, dsn=f"{host}:{port}/{service}")
            c.close()
            log.info(f"Oracle pronto dopo {(i + 1) * 5}s")
            sys.exit(0)
        except Exception as e:
            log.warning(f"tentativo {i + 1}: {e}")

        time.sleep(5)

    log.error("TIMEOUT dopo 10 minuti")
    sys.exit(1)
