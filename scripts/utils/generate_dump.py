import glob
import datetime
import logging
import os

log = logging.getLogger(__name__)

def generate_dump():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"-- Dump generated on: {now}\n\n"
    
    files = sorted(glob.glob('db/*.sql'))
    if not files:
        log.warning("No SQL files found in db/ directory.")
        return

    content = header
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            content += f"-- Source: {os.path.basename(f)}\n"
            content += fp.read()
            if not content.endswith('\n'):
                content += '\n'
            content += "\n"
            
    with open('dump.sql', 'w', encoding='utf-8') as fp:
        fp.write(content)
        
    log.info("Dump generated successfully in dump.sql")
