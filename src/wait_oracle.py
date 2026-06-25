import sys
import socket
import time
import oracledb

host = "localhost"
port = 1521
password = sys.argv[1]
service = sys.argv[2] if len(sys.argv) > 2 else "FREEPDB1"

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
        print(f"ready after {(i + 1) * 5}s")
        sys.exit(0)
    except Exception as e:
        print(f"attempt {i + 1}: {e}", file=sys.stderr)

    time.sleep(5)

print("timeout after 10 minutes", file=sys.stderr)
sys.exit(1)
