import sys
import logging
import oracledb

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def verify_records(password):
    conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
    cur = conn.cursor()

    log.info("DATA VERIFICATION START")

    tables = [
        "PERSONA","PERSONALE","PARENTE","TUTORE","OPERATORE","CONTRATTO",
        "MEDICO","REPARTO","CAMERA","RESIDENTE","MALATTIA","FARMACO",
        "TRATTAMENTO","SOFFRE","ASSUME","PAI","NECESSITA",
        "AZIENDA_ESTERNA","DITTA_PULIZIE","DITTA_RISTORANTE","DIETA","FORNISCE","PULISCE",
        "DOCUMENTO","ENTE","PRENOTAZIONE",
        "TURNO_PROGRAMMATO","TURNO_EFFETTUATO","VISITA","CONSULENZA",
        "RICEVE","EFFETTUA"
    ]

    total = 0
    empty = []
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        total += count
        if count == 0:
            empty.append(t)
            log.warning(f"{t} EMPTY")
        else:
            log.info(f"{t} {count} records")

    log.info(f"Tables {len(tables)} Total records {total} Empty {len(empty)}")
    if empty:
        log.error(f"STATUS ERROR {', '.join(empty)} empty")
        sys.exit(1)
    log.info("STATUS OK")

    cur.close()
    conn.close()
