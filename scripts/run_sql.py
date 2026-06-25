import re
import sys
import logging
import oracledb

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def execute_sql(password, sql_file):
    conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
    cur = conn.cursor()

    with open(sql_file) as f:
        sql = f.read()

    basename = sql_file.split("/")[-1]
    log.info(f"{basename} INIZIO")
    log.info(f"{basename} Connessione OK")

    ok = 0
    fail = 0

    blocks = re.split(r'\n/\s*\n', sql)
    for block in blocks:
        s = block.strip()
        if not s:
            continue
        if re.match(r'CREATE\s+OR\s+REPLACE', s, re.IGNORECASE):
            name_match = re.search(r'(FUNCTION|TRIGGER|PACKAGE|PROCEDURE)\s+(\S+)', s, re.IGNORECASE)
            obj_type = name_match.group(1) if name_match else "OGGETTO"
            obj_name = name_match.group(2) if name_match else s[:40]
            try:
                cur.execute(s)
                ok += 1
                log.info(f"{basename} {obj_type} {obj_name} CREATO")
            except oracledb.Error as e:
                fail += 1
                log.error(f"{basename} {obj_type} {obj_name} ERRORE: {e}")
        else:
            stmts = [x.strip() for x in s.split(";") if x.strip()]
            for stmt in stmts:
                upper = stmt.strip().upper()
                try:
                    cur.execute(stmt)
                    ok += 1
                except oracledb.Error as e:
                    if "ORA-00942" in str(e) and upper.startswith("DROP"):
                        ok += 1
                    else:
                        fail += 1
                        first_line = stmt.split("\n")[0][:80]
                        log.error(f"{basename} ERRORE: {first_line} -> {e}")

    if fail == 0:
        conn.commit()
        log.info(f"{basename} COMMIT transazione completata")
        log.info(f"{basename} STATO OK {ok} statement")
    else:
        conn.rollback()
        log.warning(f"{basename} ROLLBACK {fail} errori")
        log.info(f"{basename} STATO ERRORE {ok} ok {fail} falliti")

    cur.close()
    conn.close()

if __name__ == "__main__":
    execute_sql(sys.argv[1], sys.argv[2])
