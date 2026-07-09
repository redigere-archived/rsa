import sys
import logging
import oracledb
from scripts.utils.config import load_config, get_dsn, get_db_user

log = logging.getLogger(__name__)

def verify_records(password):
    cfg = load_config()
    conn = oracledb.connect(user=get_db_user(cfg), password=password, dsn=get_dsn(cfg))
    cur = conn.cursor()

    log.info("data verification start")

    tables = cfg["tables"]
    total = 0
    empty = []
    for t in tables:
        log.info(f"verify: SELECT COUNT(*) FROM {t}")
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        total += count
        log.info(f"verify: {t} -> {count} records")
        if count == 0:
            empty.append(t)
            log.warning(f"{t} empty")
        else:
            log.info(f"{t} {count} records")

    log.info(f"tables {len(tables)} total records {total} empty {len(empty)}")
    if empty:
        log.error(f"status error {', '.join(empty)} empty")
        for e in empty:
            log.error(f"  empty table: {e}")
        sys.exit(1)
    log.info("status ok")

    cur.close()
    conn.close()
