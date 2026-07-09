import sys
import logging
import oracledb
from scripts.utils.config import load_config, get_dsn, get_db_user, get_db_owner

log = logging.getLogger(__name__)

def verify_schema(password):
    cfg = load_config()
    conn = oracledb.connect(user=get_db_user(cfg), password=password, dsn=get_dsn(cfg))
    cur = conn.cursor()

    log.info("SCHEMA VERIFICATION START")

    expected_tables = cfg["schema_tables"]
    sc = cfg["schema"]
    exclude_patterns = sc["exclude_table_patterns"]
    owner = sc.get("owner", get_db_owner(cfg))

    exclude_sql = " AND ".join(f"TABLE_NAME NOT LIKE '{p}'" for p in exclude_patterns)
    errors = []

    cur.execute(f"SELECT TABLE_NAME FROM USER_TABLES WHERE {exclude_sql}")
    existing_tables = {row[0] for row in cur.fetchall()}

    for table_name in sorted(expected_tables.keys()):
        log.info(f"SCHEMA: checking table {table_name}")
        if table_name not in existing_tables:
            errors.append(f"MISSING TABLE {table_name}")
            log.error(f"{table_name} MISSING")
            continue

        log.info(f"SCHEMA: SELECT COLUMN_NAME, DATA_TYPE FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{table_name}'")
        cur.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{table_name}' AND OWNER = '{owner}'")
        columns = {row[0]: row[1] for row in cur.fetchall()}
        log.info(f"SCHEMA: {table_name} columns found: {list(columns.keys())}")

        for col_name, col_type in expected_tables[table_name].items():
            log.info(f"SCHEMA: checking column {table_name}.{col_name} expected type {col_type}")
            if col_name not in columns:
                errors.append(f"MISSING COLUMN {table_name}.{col_name}")
                log.error(f"{table_name}.{col_name} MISSING")
            elif not columns[col_name].startswith(col_type):
                errors.append(f"WRONG TYPE {table_name}.{col_name} expected {col_type} found {columns[col_name]}")
                log.error(f"{table_name}.{col_name} WRONG TYPE {columns[col_name]}")
            else:
                log.info(f"SCHEMA: {table_name}.{col_name} OK ({columns[col_name]})")

        log.info(f"SCHEMA: SELECT COUNT(*) FROM {table_name}")
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        log.info(f"SCHEMA: {table_name} COUNT(*) = {count}")
        if count == 0:
            log.warning(f"{table_name} EMPTY TABLE")
        else:
            log.info(f"{table_name} OK {count} records")

    cur.execute(f"SELECT COUNT(*) FROM USER_TRIGGERS WHERE TRIGGER_NAME LIKE '{sc['trigger_name_pattern']}'")
    trg_count = cur.fetchone()[0]
    log.info(f"TRIGGERS FOUND {trg_count}")

    fn_prefixes = " OR ".join(f"OBJECT_NAME LIKE '{p}'" for p in sc["function_prefix_patterns"])
    cur.execute(f"SELECT COUNT(*) FROM USER_OBJECTS WHERE OBJECT_TYPE = 'FUNCTION' AND ({fn_prefixes})")
    fn_count = cur.fetchone()[0]
    log.info(f"FUNCTIONS FOUND {fn_count}")

    constraint_types = ",".join(f"'{t}'" for t in sc["constraint_types"])
    cur.execute(f"SELECT COUNT(*) FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE IN ({constraint_types}) AND {exclude_sql}")
    cst_count = cur.fetchone()[0]
    log.info(f"PK/FK CONSTRAINTS {cst_count}")

    if errors:
        log.error(f"STATUS ERROR {len(errors)} issues")
        for e in errors:
            log.error(f"  {e}")
        sys.exit(1)
    else:
        log.info(f"STATUS OK tables {len(expected_tables)} triggers {trg_count} functions {fn_count} constraints {cst_count}")

    cur.close()
    conn.close()
