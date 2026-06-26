import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def verify_signoff():
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%s"],
        capture_output=True, text=True
    )
    last_msg = result.stdout.strip()

    if last_msg.startswith("log:"):
        log.info("Skipping log commit")
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
            log.error(f"MISSING {sha[:8]} {subject}")
            failed += 1

    if failed:
        log.error(f"STATUS ERROR {failed} commits without signoff")
        sys.exit(1)

    log.info("STATUS OK")
