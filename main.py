import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def print_usage():
    log.info("RSA Database Manager")
    log.info("Uso: python3 main.py <comando> [argomenti]")
    log.info("Comandi:")
    log.info("  run <password> <file.sql>     Esegui file SQL")
    log.info("  wait <password>               Attendi Oracle XE")
    log.info("  verify <password>             Verifica record")
    log.info("  schema <password>             Verifica struttura")
    log.info("  report <password>             Genera report")
    log.info("  signoff                       Verifica signoff git")
    log.info("  all <password>                Esegui tutto")

def run_all(password):
    from run_sql import execute_sql
    from verify import verify_records
    from verify_schema import verify_schema
    from report import generate_report

    steps = [
        ("DDL", "db/01_ddl.sql"),
        ("DML", "db/02_dml.sql"),
        ("Functions", "db/03_functions.sql"),
        ("Triggers", "db/04_triggers.sql"),
    ]

    for name, sql_file in steps:
        execute_sql(password, sql_file)

    verify_records(password)
    verify_schema(password)
    generate_report(password)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "signoff":
        from verify_signoff import verify_signoff
        verify_signoff()
    elif command == "wait":
        from wait_oracle import wait_for_oracle
        wait_for_oracle(sys.argv[2])
    elif command == "run":
        from run_sql import execute_sql
        execute_sql(sys.argv[2], sys.argv[3])
    elif command == "verify":
        from verify import verify_records
        verify_records(sys.argv[2])
    elif command == "schema":
        from verify_schema import verify_schema
        verify_schema(sys.argv[2])
    elif command == "report":
        from report import generate_report
        generate_report(sys.argv[2])
    elif command == "all":
        run_all(sys.argv[2])
    else:
        log.error(f"Comando sconosciuto {command}")
        print_usage()
        sys.exit(1)
