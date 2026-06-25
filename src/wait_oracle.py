import sys
import socket
import time
import oracledb

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
            print(f"[WAIT] Oracle pronto dopo {(i + 1) * 5}s")
            sys.exit(0)
        except Exception as e:
            print(f"[WAIT] tentativo {i + 1}: {e}", file=sys.stderr)

        time.sleep(5)

    print("[WAIT] TIMEOUT dopo 10 minuti", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    wait_for_oracle(sys.argv[1])
