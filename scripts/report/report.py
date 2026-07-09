import logging
import oracledb
from scripts.utils.config import load_config, get_dsn, get_db_user

log = logging.getLogger(__name__)

def generate_report(password):
    cfg = load_config()
    conn = oracledb.connect(user=get_db_user(cfg), password=password, dsn=get_dsn(cfg))
    cur = conn.cursor()

    log.info("RSA REPORT DATABASE")

    tables = cfg["tables"]
    total = 0
    for t in tables:
        log.info(f"REPORT: SELECT COUNT(*) FROM {t}")
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        total += count
        log.info(f"REPORT: {t} -> {count}")
        log.info(f"{t} {count}")
    log.info(f"TOTAL {total}")

    for entry in cfg["reports"]["queries"]:
        title = entry["name"]
        sql = entry["sql"]
        log.info(f"REPORT: executing function query - {title}")
        log.info(f"REPORT: SQL: {sql[:200]}")
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            log.info(f"REPORT: {title} returned {len(rows)} rows")
            for row in rows:
                log.info(f"{title} {row}")
        except Exception as e:
            log.error(f"{title} Error {e}")

    trg_pattern = cfg["schema"]["trigger_name_pattern"]
    cur.execute(f"SELECT TRIGGER_NAME, TABLE_NAME, STATUS FROM USER_TRIGGERS WHERE TRIGGER_NAME LIKE '{trg_pattern}' ORDER BY TABLE_NAME")
    for name, table, status in cur.fetchall():
        log.info(f"TRIGGER {name} {table} {status}")

    log.info("STATUS COMPLETED")
    cur.close()
    conn.close()
