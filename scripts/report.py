import logging
import oracledb

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def generate_report(password):
    conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
    cur = conn.cursor()

    log.info("RSA REPORT DATABASE")

    tables = [
        "PERSONA","PERSONALE","PARENTE","TUTORE","OPERATORE","CONTRATTO",
        "MEDICO","REPARTO","CAMERA","RESIDENTE","MALATTIA","FARMACO",
        "TRATTAMENTO","SOFFRE","ASSUME","PAI","NECESSITA","AZIENDA_ESTERNA",
        "DITTA_PULIZIE","DITTA_RISTORANTE","FORNISCE","PULISCE",
        "DOCUMENTO","ENTE","PRENOTAZIONE",
        "TURNO_PROGRAMMATO","TURNO_EFFETTUATO","VISITA","CONSULENZA",
        "RICEVE","EFFETTUA"
    ]
    total = 0
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        total += count
        log.info(f"{t} {count}")
    log.info(f"TOTALE {total}")

    funcs = [
        ("ETA RESIDENTI", "SELECT P.NOME, P.COGNOME, CALCOLA_ETA(R.CODICE_FISCALE) FROM RESIDENTE R JOIN PERSONA P ON R.CODICE_FISCALE = P.CODICE_FISCALE"),
        ("CAMERE LIBERE", "SELECT NOME_REPARTO, CONTEGGIO_CAMERE_LIBERE(CODICE_REPARTO) FROM REPARTO"),
        ("FARMACI ASSEGNATI", "SELECT P.NOME, P.COGNOME, CONTEGGIO_FARMACI_ASSEGNATI(R.CODICE_FISCALE) FROM RESIDENTE R JOIN PERSONA P ON R.CODICE_FISCALE = P.CODICE_FISCALE"),
        ("STIPENDIO MESE", "SELECT P.NOME, P.COGNOME, CALCOLA_STIPENDIO_MENSILE(P.CODICE_FISCALE) FROM PERSONALE PE JOIN PERSONA P ON PE.CODICE_FISCALE = P.CODICE_FISCALE"),
        ("PAI ATTIVI", "SELECT P.NOME, P.COGNOME, VERIFICA_PAI_ATTIVO(R.CODICE_FISCALE) FROM RESIDENTE R JOIN PERSONA P ON R.CODICE_FISCALE = P.CODICE_FISCALE"),
        ("ESITO TRATTAMENTI", "SELECT CODICE_TRATTAMENTO, DESCRIZIONE_ESITO_TRATTAMENTO(CODICE_TRATTAMENTO) FROM TRATTAMENTO"),
        ("NUMERO VISITE", "SELECT P.NOME, P.COGNOME, CONTEGGIO_VISITE_RESIDENTE(R.CODICE_FISCALE, TO_DATE('2025-01-01','YYYY-MM-DD'), TO_DATE('2025-12-31','YYYY-MM-DD')) FROM RESIDENTE R JOIN PERSONA P ON R.CODICE_FISCALE = P.CODICE_FISCALE"),
    ]
    for title, sql in funcs:
        try:
            cur.execute(sql)
            for row in cur.fetchall():
                log.info(f"{title} {row}")
        except Exception as e:
            log.error(f"{title} Errore {e}")

    cur.execute("SELECT TRIGGER_NAME, TABLE_NAME, STATUS FROM USER_TRIGGERS WHERE TRIGGER_NAME LIKE 'TRG_%' ORDER BY TABLE_NAME")
    for name, table, status in cur.fetchall():
        log.info(f"TRIGGER {name} {table} {status}")

    log.info("STATO COMPLETATO")
    cur.close()
    conn.close()
