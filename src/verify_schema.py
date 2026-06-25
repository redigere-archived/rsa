import sys
import oracledb

password = sys.argv[1]

conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
cur = conn.cursor()

print("[SCHEMA] INIZIO VERIFICA STRUTTURA")
print()

expected_tables = {
    "PERSONA": {"CODICE_FISCALE": "VARCHAR2", "NOME": "VARCHAR2", "COGNOME": "VARCHAR2", "DATA_NASCITA": "DATE"},
    "PERSONALE": {"CODICE_FISCALE": "VARCHAR2"},
    "PARENTE": {"CODICE_FISCALE": "VARCHAR2"},
    "TUTORE": {"CODICE_FISCALE": "VARCHAR2"},
    "OPERATORE": {"CODICE_FISCALE": "VARCHAR2"},
    "CONTRATTO": {"CODICE_CONTRATTO": "NUMBER", "PAGA_ORARIA": "NUMBER", "TIPO_CONTRATTO": "VARCHAR2"},
    "MEDICO": {"CODICE_FISCALE": "VARCHAR2", "CODICE_CONTRATTO": "NUMBER"},
    "REPARTO": {"CODICE_REPARTO": "VARCHAR2", "NOME_REPARTO": "VARCHAR2"},
    "CAMERA": {"NUMERO_CAMERA": "NUMBER", "PIANO": "NUMBER", "LETTI_TOTALI": "NUMBER"},
    "RESIDENTE": {"CODICE_FISCALE": "VARCHAR2", "NUMERO_CAMERA": "NUMBER"},
    "MALATTIA": {"CODICE": "VARCHAR2", "NOME": "VARCHAR2", "LIVELLO": "VARCHAR2"},
    "FARMACO": {"CODICE_FARMACO": "VARCHAR2", "DOSE": "NUMBER", "NOME": "VARCHAR2"},
    "TRATTAMENTO": {"CODICE_TRATTAMENTO": "VARCHAR2", "RAGGIUNTO": "CHAR"},
    "SOFFRE": {"CODICE": "VARCHAR2", "CODICE_FISCALE": "VARCHAR2"},
    "ASSUME": {"CODICE_FARMACO": "VARCHAR2", "CODICE_FISCALE": "VARCHAR2"},
    "PAI": {"CODICE_PAI": "VARCHAR2", "CODICE_FISCALE_RESIDENTE": "VARCHAR2"},
    "NECESSITA": {"CODICE_TRATTAMENTO": "VARCHAR2", "CODICE_PAI": "VARCHAR2"},
    "AZIENDA_ESTERNA": {"PARTITA_IVA": "VARCHAR2", "EMAIL": "VARCHAR2", "NOME_AZIENDA": "VARCHAR2"},
    "DITTA": {"PARTITA_IVA": "VARCHAR2", "NOME": "VARCHAR2", "TIPOLOGIA": "VARCHAR2"},
    "FORNITORE": {"PARTITA_IVA": "VARCHAR2", "NOME": "VARCHAR2"},
    "DITTA_PULIZIA": {"PARTITA_IVA": "VARCHAR2"},
    "DITTA_RISTORANTE": {"PARTITA_IVA": "VARCHAR2"},
    "FORNISCE": {"PARTITA_IVA": "VARCHAR2", "NUMERO_CAMERA": "NUMBER"},
    "PULISCE": {"NUMERO_CAMERA": "NUMBER", "PARTITA_IVA": "VARCHAR2"},
    "DOCUMENTO": {"CODICE_PRENOTAZIONE": "VARCHAR2", "PARTITA_IVA": "VARCHAR2"},
    "ENTE": {"PARTITA_IVA": "VARCHAR2", "ENTE_EROGAZIONE": "VARCHAR2"},
    "PRENOTAZIONE": {"CODICE_PRENOTAZIONE": "VARCHAR2"},
    "TURNO_PROGRAMMATO": {"ORA_INIZIO": "VARCHAR2", "ORA_FINE": "VARCHAR2", "GIORNO": "DATE"},
    "TURNO_EFFETTUATO": {"ORA_INIZIO": "VARCHAR2", "ORA_FINE": "VARCHAR2", "GIORNO": "DATE"},
    "VISITA": {"CODICE_FISCALE": "VARCHAR2", "GIORNO_VISITA": "DATE", "ORA_INGRESSO": "VARCHAR2"},
    "CONSULENZA": {"DATA_CONSULENZA": "DATE"},
    "RICEVE": {"CODICE_FISCALE": "VARCHAR2", "DATA_CONSULENZA": "DATE"},
    "EFFETTUA": {"DATA_CONSULENZA": "DATE", "CODICE_FISCALE": "VARCHAR2"},
}

errors = []

cur.execute("SELECT TABLE_NAME FROM USER_TABLES WHERE TABLE_NAME NOT LIKE 'SYS_%' AND TABLE_NAME NOT LIKE 'AQ_%' AND TABLE_NAME NOT LIKE 'HELP%' AND TABLE_NAME NOT LIKE 'BIN_%' AND TABLE_NAME NOT LIKE 'MVIEW%'")
existing_tables = {row[0] for row in cur.fetchall()}

for table_name in sorted(expected_tables.keys()):
    if table_name not in existing_tables:
        errors.append(f"TABELLA MANCANTE: {table_name}")
        print(f"[SCHEMA] {table_name}: MANCANTE")
        continue

    cur.execute(f"SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{table_name}' AND OWNER = 'SYSTEM'")
    columns = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    for col_name, col_type in expected_tables[table_name].items():
        if col_name not in columns:
            errors.append(f"COLUMN MANCANTE: {table_name}.{col_name}")
            print(f"[SCHEMA] {table_name}.{col_name}: MANCANTE")
        else:
            actual_type = columns[col_name][0]
            if not actual_type.startswith(col_type):
                errors.append(f"TIPO ERRATO: {table_name}.{col_name} atteso {col_type} trovato {actual_type}")
                print(f"[SCHEMA] {table_name}.{col_name}: TIPO ERRATO ({actual_type})")

    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
    if count == 0:
        print(f"[SCHEMA] {table_name}: TABELLA VUOTA")
    else:
        print(f"[SCHEMA] {table_name}: OK ({count} record)")

print()
cur.execute("SELECT COUNT(*) FROM USER_TRIGGERS WHERE TRIGGER_NAME LIKE 'TRG_%'")
trg_count = cur.fetchone()[0]
print(f"[SCHEMA] TRIGGER TROVATI: {trg_count}")

cur.execute("SELECT COUNT(*) FROM USER_OBJECTS WHERE OBJECT_TYPE = 'FUNCTION' AND (OBJECT_NAME LIKE 'CALCOLA%' OR OBJECT_NAME LIKE 'CONTEGGIO%' OR OBJECT_NAME LIKE 'VERIFICA%' OR OBJECT_NAME LIKE 'DESCRIZIONE%')")
fn_count = cur.fetchone()[0]
print(f"[SCHEMA] FUNZIONI TROVATE: {fn_count}")

cur.execute("SELECT COUNT(*) FROM USER_CONSTRAINTS WHERE CONSTRAINT_TYPE IN ('P','R') AND TABLE_NAME NOT LIKE 'SYS_%' AND TABLE_NAME NOT LIKE 'AQ_%' AND TABLE_NAME NOT LIKE 'HELP%' AND TABLE_NAME NOT LIKE 'BIN_%' AND TABLE_NAME NOT LIKE 'MVIEW%'")
cst_count = cur.fetchone()[0]
print(f"[SCHEMA] VINCOLI PK/FK: {cst_count}")

print()
if errors:
    print(f"[SCHEMA] STATO: ERRORE ({len(errors)} problemi)")
    for e in errors:
        print(f"[SCHEMA]   {e}")
    sys.exit(1)
else:
    print(f"[SCHEMA] STATO: OK (tabelle: {len(expected_tables)}, trigger: {trg_count}, funzioni: {fn_count}, vincoli: {cst_count})")

cur.close()
conn.close()
