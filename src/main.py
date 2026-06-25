import sys

def print_usage():
    print("RSA Database Manager")
    print()
    print("Uso: python3 src/main.py <comando> [argomenti]")
    print()
    print("Comandi:")
    print("  run <password> <file.sql>     Esegui file SQL")
    print("  wait <password>               Attendi Oracle XE")
    print("  verify <password>             Verifica record")
    print("  schema <password>             Verifica struttura")
    print("  report <password>             Genera report")
    print("  signoff                       Verifica signoff git")
    print("  all <password>                Esegui tutto (DDL DML Functions Triggers Verify Report)")

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
        print(f"\n{'=' * 50}")
        print(f"  {name}")
        print(f"{'=' * 50}")
        execute_sql(password, sql_file)

    print(f"\n{'=' * 50}")
    print(f"  Verify Records")
    print(f"{'=' * 50}")
    verify_records(password)

    print(f"\n{'=' * 50}")
    print(f"  Verify Schema")
    print(f"{'=' * 50}")
    verify_schema(password)

    print(f"\n{'=' * 50}")
    print(f"  Report")
    print(f"{'=' * 50}")
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
        print(f"Comando sconosciuto: {command}")
        print_usage()
        sys.exit(1)
