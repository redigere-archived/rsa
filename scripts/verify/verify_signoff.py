import subprocess
import sys
import logging
from scripts.utils.config import load_config

log = logging.getLogger(__name__)

def verify_signoff():
    cfg = load_config()
    signoff = cfg["signoff"]
    skip_prefix = signoff["skip_prefix"]
    tag = signoff["tag"]

    result = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%s"],
        capture_output=True, text=True
    )
    last_msg = result.stdout.strip()

    if last_msg.startswith(skip_prefix):
        log.info(f"Skipping {skip_prefix} commit")
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
        if tag not in msg:
            subject = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%s", sha],
                capture_output=True, text=True
            ).stdout.strip()
            log.error(f"MISSING {sha[:8]} {subject}")
            failed += 1

    if failed:
        log.error(f"STATUS ERROR {failed} commits without {tag}")
        sys.exit(1)

    log.info("STATUS OK")
