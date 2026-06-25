import subprocess
import sys

def verify_signoff():
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%s"],
        capture_output=True, text=True
    )
    last_msg = result.stdout.strip()

    if last_msg.startswith("log:"):
        print("[SIGNOFF] Skip per commit log")
        sys.exit(0)

    result = subprocess.run(
        ["git", "log", "--pretty=format:%H"],
        capture_output=True, text=True
    )

    failed = 0
    for sha in result.stdout.strip().split("\n"):
        if not sha:
            continue
        msg_result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%B", sha],
            capture_output=True, text=True
        )
        msg = msg_result.stdout
        if "Signed-off-by:" not in msg:
            subject = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%s", sha],
                capture_output=True, text=True
            ).stdout.strip()
            print(f"[SIGNOFF] MANCANTE: {sha[:8]} {subject}")
            failed += 1

    if failed:
        print(f"[SIGNOFF] STATO: ERRORE ({failed} commit senza signoff)")
        sys.exit(1)

    print("[SIGNOFF] STATO: OK")

if __name__ == "__main__":
    verify_signoff()
