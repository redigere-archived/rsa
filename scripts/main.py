import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def run_all(password):
    from run_sql import execute_sql
    from verify import verify_records
    from verify_schema import verify_schema
    from report import generate_report

    for sql_file in ["db/01_ddl.sql", "db/02_dml.sql", "db/03_functions.sql", "db/04_triggers.sql"]:
        execute_sql(password, sql_file)

    verify_records(password)
    verify_schema(password)
    generate_report(password)

if __name__ == "__main__":
    command = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "signoff":
        from verify_signoff import verify_signoff
        verify_signoff()
    elif command == "wait":
        from wait_oracle import wait_for_oracle
        wait_for_oracle(password)
    elif command == "run":
        from run_sql import execute_sql
        execute_sql(password, sys.argv[3])
    elif command == "verify":
        from verify import verify_records
        verify_records(password)
    elif command == "schema":
        from verify_schema import verify_schema
        verify_schema(password)
    elif command == "report":
        from report import generate_report
        generate_report(password)
    elif command == "all":
        run_all(password)
