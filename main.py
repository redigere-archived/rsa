import sys
import logging
from scripts.utils.config import load_config

cfg = load_config()
log_cfg = cfg["logging"]
logging.basicConfig(level=getattr(logging, log_cfg["level"]), format=log_cfg["format"])
log = logging.getLogger(__name__)

def run_all(password):
    from scripts.db.run_sql import execute_sql
    from scripts.verify.verify import verify_records
    from scripts.verify.verify_schema import verify_schema
    from scripts.report.report import generate_report

    for sql_file in cfg["paths"]["sql_files"]:
        execute_sql(password, sql_file)

    verify_records(password)
    verify_schema(password)
    generate_report(password)

if __name__ == "__main__":
    command = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "signoff":
        from scripts.verify.verify_signoff import verify_signoff
        verify_signoff()
    elif command == "wait":
        from scripts.utils.wait_oracle import wait_for_oracle
        wait_for_oracle(password)
    elif command == "run":
        from scripts.db.run_sql import execute_sql
        execute_sql(password, sys.argv[3])
    elif command == "verify":
        from scripts.verify.verify import verify_records
        verify_records(password)
    elif command == "schema":
        from scripts.verify.verify_schema import verify_schema
        verify_schema(password)
    elif command == "report":
        from scripts.report.report import generate_report
        generate_report(password)
    elif command == "dump":
        from scripts.utils.generate_dump import generate_dump
        generate_dump()
    elif command == "all":
        run_all(password)
