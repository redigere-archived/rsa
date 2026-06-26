import sys
import logging
import oracledb

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def verify_schema(password):
    conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
    cur = conn.cursor()

    log.info("SCHEMA VERIFICATION START")

    expected_tables = {
        "PERSONA": {"CODICE_FISCALE": "VARCHAR2", "NOME": "VARCHAR2", "COGNOME": "VARCHAR2", "DATA_NASCITA": "DATE"},
        "PERSONALE": {"CODICE_FISCALE": "VARCHAR2"},
        "PARENTE": {"CODICE_FISCALE": "VARCHAR2"},
        "TUTORE": {"CODICE_FISCALE": "VARCHAR2"},
        "OPERATORE": {"CODICE_FISCALE": "VARCHAR2"},
        "CONTRATTO": {"CODICE_CONTRATTO": "NUMBER", "TIPO_CONTRATTO": "VARCHAR2", "PAGA_ORARIA": "NUMBER", "TASSA_DETRATTA": "NUMBER", "CODICE_FISCALE_PERSONALE": "VARCHAR2"},
        "MEDICO": {"CODICE_FISCALE": "VARCHAR2", "CODICE_CONTRATTO": "NUMBER"},
        "REPARTO": {"CODICE_REPARTO": "VARCHAR2", "NOME_REPARTO": "VARCHAR2", "CODICE_RESPONSABILE": "VARCHAR2"},
        "CAMERA": {"NUMERO_CAMERA": "NUMBER", "PIANO": "NUMBER", "LETTI_TOTALI": "NUMBER", "CODICE_REPARTO": "VARCHAR2"},
        "RESIDENTE": {"CODICE_FISCALE": "VARCHAR2", "NUMERO_CAMERA": "NUMBER"},
        "MALATTIA": {"CODICE": "VARCHAR2", "NOME": "VARCHAR2", "DESCRIZIONE": "CLOB", "LIVELLO": "VARCHAR2"},
        "FARMACO": {"CODICE_FARMACO": "VARCHAR2", "NOME": "VARCHAR2", "DOSE": "NUMBER", "FASCIA_ORARIA": "VARCHAR2"},
        "TRATTAMENTO": {"CODICE_TRATTAMENTO": "VARCHAR2", "OBIETTIVO": "CLOB", "ESITO": "CLOB", "RAGGIUNTO": "CHAR"},
        "SOFFRE": {"CODICE": "VARCHAR2", "CODICE_FISCALE": "VARCHAR2"},
        "ASSUME": {"CODICE_FARMACO": "VARCHAR2", "CODICE_FISCALE": "VARCHAR2"},
        "PAI": {"CODICE_PAI": "VARCHAR2", "CODICE_FISCALE_RESIDENTE": "VARCHAR2", "DATA_REDAZIONE": "DATE", "DATA_REVISIONE": "DATE", "DIAGNOSI": "CLOB", "DATA_DIMISSIONE": "DATE"},
        "NECESSITA": {"CODICE_TRATTAMENTO": "VARCHAR2", "CODICE_PAI": "VARCHAR2"},
        "RISOLVE": {"CODICE_TRATTAMENTO": "VARCHAR2", "CODICE_OSS": "VARCHAR2"},
        "AZIENDA_ESTERNA": {"PARTITA_IVA": "VARCHAR2", "NOME_AZIENDA": "CLOB", "EMAIL": "CLOB", "NUMERO_DI_TELEFONO": "VARCHAR2", "PEC": "CLOB", "CODICE_FISCALE_OPERATORE": "VARCHAR2"},
        "DITTA_PULIZIE": {"PARTITA_IVA": "VARCHAR2"},
        "DITTA_RISTORANTE": {"PARTITA_IVA": "VARCHAR2"},
        "DIETA": {"NOME": "VARCHAR2", "TIPOLOGIA": "VARCHAR2", "NOTE": "VARCHAR2"},
        "FORNISCE": {"PARTITA_IVA": "VARCHAR2", "NOME": "VARCHAR2"},
        "PULISCE": {"NUMERO_CAMERA": "NUMBER", "PARTITA_IVA": "VARCHAR2"},
        "DOCUMENTO": {"CODICE_FISCALE": "VARCHAR2", "SCADENZA": "DATE", "PARTITA_IVA": "VARCHAR2"},
        "ENTE": {"PARTITA_IVA": "VARCHAR2", "NOME_ISTITUZIONE": "VARCHAR2"},
        "PRENOTAZIONE": {"CODICE_PRENOTAZIONE": "NUMBER", "DESCRIZIONE": "CLOB", "DATA_PRENOTAZIONE": "DATE", "DATA_DIMISSIONE": "DATE", "NUMERO_CAMERA": "NUMBER", "CODICE_FISCALE_TUTORE": "VARCHAR2"},
        "TURNO_PROGRAMMATO": {"CODICE_FISCALE_MEDICO": "VARCHAR2", "DATA_INIZIO": "DATE", "DATA_FINE": "DATE", "GIORNO": "VARCHAR2", "FASCIA_ORARIA": "VARCHAR2"},
        "TURNO_EFFETTUATO": {"FASCIA_ORARIA": "VARCHAR2", "ORA_INIZIO": "VARCHAR2", "ORA_FINE": "VARCHAR2", "GIORNO": "DATE", "CODICE_FISCALE_MEDICO": "VARCHAR2"},
        "VISITA": {"CODICE_FISCALE_PARENTE": "VARCHAR2", "GIORNO_VISITA": "DATE", "ORA_INGRESSO": "VARCHAR2", "ORA_USCITA": "VARCHAR2", "CODICE_FISCALE_RESIDENTE": "VARCHAR2"},
        "CONSULENZA": {"DATA_CONSULENZA": "DATE", "NOTE_CONSULENZA": "CLOB"},
        "RICEVE": {"CODICE_PAI": "VARCHAR2", "DATA_CONSULENZA": "DATE"},
        "EFFETTUA": {"DATA_CONSULENZA": "DATE", "CODICE_FISCALE_MEDICO": "VARCHAR2"},
    }

    errors = []

    cur.execute("SELECT TABLE_NAME FROM USER_TABLES WHERE TABLE_NAME NOT LIKE 'SYS_%' AND TABLE_NAME NOT LIKE 'AQ_%' AND TABLE_NAME NOT LIKE 'HELP%' AND TABLE_NAME NOT LIKE 'BIN_%' AND TABLE_NAME NOT LIKE 'MVIEW%'")
    existing_tables = {row[0] for row in cur.fetchall()}

    for table_name in sorted(expected_tables.keys()):
        if table_name not in existing_tables:
            errors.append(f"MISSING TABLE {table_name}")
            log.error(f"{table_name} MISSING")
            continue

        cur.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{table_name}' AND OWNER = 'SYSTEM'")
        columns = {row[0]: row[1] for row in cur.fetchall()}

        for col_name, col_type in expected_tables[table_name].items():
            if col_name not in columns:
                errors.append(f"MISSING COLUMN {table_name}.{col_name}")
                log.error(f"{table_name}.{col_name} MISSING")
            elif not columns[col_name].startswith(col_type):
                errors.append(f"WRONG TYPE {table_name}.{col_name} expected {col_type} found {columns[col_name]}")
                log.error(f"{table_name}.{col_name} WRONG TYPE {columns[col_name]}")

        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        if count == 0:
            log.warning(f"{table_name} EMPTY TABLE")
        else:
            log.info(f"{table_name} OK {count} records")

    cur.execute("SELECT COUNT(*) FROM USER_TRIGGERS WHERE TRIGGER_NAME LIKE 'TRG_%'")
    trg_count = cur.fetchone()[0]
    log.info(f"TRIGGERS FOUND {trg_count}")

    cur.execute("SELECT COUNT(*) FROM USER_OBJECTS WHERE OBJECT_TYPE = 'FUNCTION' AND (OBJECT_NAME LIKE 'CALCOLA%' OR OBJECT_NAME LIKE 'CONTEGGIO%' OR OBJECT_NAME LIKE 'VERIFICA%' OR OBJECT_NAME LIKE 'DESCRIZIONE%')")
    fn_count = cur.fetchone()[0]
    log.info(f"FUNCTIONS FOUND {fn_count}")

    cur.execute("SELECT COUNT(*) FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE IN ('P','R') AND TABLE_NAME NOT LIKE 'SYS_%' AND TABLE_NAME NOT LIKE 'AQ_%' AND TABLE_NAME NOT LIKE 'HELP%' AND TABLE_NAME NOT LIKE 'BIN_%' AND TABLE_NAME NOT LIKE 'MVIEW%'")
    cst_count = cur.fetchone()[0]
    log.info(f"PK/FK CONSTRAINTS {cst_count}")

    if errors:
        log.error(f"STATUS ERROR {len(errors)} issues")
        for e in errors:
            log.error(f"  {e}")
        sys.exit(1)
    else:
        log.info(f"STATUS OK tables {len(expected_tables)} triggers {trg_count} functions {fn_count} constraints {cst_count}")

    cur.close()
    conn.close()
