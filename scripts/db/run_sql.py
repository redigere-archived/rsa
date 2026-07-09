import re
import logging
import oracledb
from scripts.utils.config import load_config, get_dsn, get_db_user

log = logging.getLogger(__name__)

def execute_sql(password, sql_file):
    cfg = load_config()
    conn = oracledb.connect(user=get_db_user(cfg), password=password, dsn=get_dsn(cfg))
    cur = conn.cursor()

    with open(sql_file) as f:
        sql = f.read()

    basename = sql_file.split("/")[-1]
    log.info(f"{basename} start")
    log.info(f"{basename} connection ok")

    ok = 0
    fail = 0

    blocks = re.split(r'\n/\s*\n', sql)
    for block in blocks:
        s = block.strip()
        if not s:
            continue
        if re.match(r'CREATE\s+OR\s+REPLACE', s, re.IGNORECASE):
            name_match = re.search(r'(FUNCTION|TRIGGER|PACKAGE|PROCEDURE)\s+(\S+)', s, re.IGNORECASE)
            obj_type = name_match.group(1) if name_match else "OBJECT"
            obj_name = name_match.group(2) if name_match else s[:40]
            log.info(f"{basename} executing: CREATE OR REPLACE {obj_type} {obj_name}")
            try:
                cur.execute(s)
                ok += 1
                log.info(f"{basename} {obj_type} {obj_name} created")
            except oracledb.Error as e:
                fail += 1
                log.error(f"{basename} {obj_type} {obj_name} error: {e}")
        else:
            stmts = [x.strip() for x in s.split(";") if x.strip()]
            for stmt in stmts:
                upper = stmt.strip().upper()
                log.info(f"{basename} executing: {stmt.split(chr(10))[0][:120]}")
                try:
                    cur.execute(stmt)
                    ok += 1
                    log.info(f"{basename} ok: {stmt.split(chr(10))[0][:80]}")
                except oracledb.Error as e:
                    if "ORA-00942" in str(e) and upper.startswith("DROP"):
                        ok += 1
                        log.info(f"{basename} ok (table not exist): {stmt.split(chr(10))[0][:80]}")
                    else:
                        fail += 1
                        first_line = stmt.split("\n")[0][:80]
                        log.error(f"{basename} error: {first_line} -> {e}")

    if fail == 0:
        conn.commit()
        log.info(f"{basename} Transaction committed")
        log.info(f"{basename} status ok {ok} statements")
    else:
        conn.rollback()
        log.warning(f"{basename} rollback {fail} errors")
        log.info(f"{basename} status error {ok} ok {fail} failed")

    cur.close()
    conn.close()
