import sys
import oracledb

def generate_report(password):
    conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
    cur = conn.cursor()

    print("[REPORT] RSA - REPORT DATABASE")
    print()

    tables = [
        "PERSONA","PERSONALE","PARENTE","TUTORE","OPERATORE","CONTRATTO",
        "MEDICO","REPARTO","CAMERA","RESIDENTE","MALATTIA","FARMACO",
        "TRATTAMENTO","SOFFRE","ASSUME","PAI","NECESSITA","AZIENDA_ESTERNA",
        "DITTA_PULIZIA","DITTA_RISTORANTE","FORNISCE","PULISCE",
        "DOCUMENTO","ENTE","PRENOTAZIONE",
        "TURNO_PROGRAMMATO","TURNO_EFFETTUATO","VISITA","CONSULENZA",
        "RICEVE","EFFETTUA"
    ]
    total = 0
    print("[REPORT] TABELLE")
    print("-" * 40)
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        total += count
        print(f"  {t:<30} {count:>4}")
    print("-" * 40)
    print(f"  {'TOTALE':<30} {total:>4}")
    print()

    print("[REPORT] FUNZIONI")
    print("-" * 50)
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
        print(f"\n  {title}")
        try:
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            print("  " + "  ".join(f"{c:<22}" for c in cols))
            for row in cur.fetchall():
                print("  " + "  ".join(f"{str(v):<22}" for v in row))
        except Exception as e:
            print(f"  Errore: {e}")
    print()

    print("[REPORT] TRIGGER")
    print("-" * 70)
    cur.execute("""
      SELECT TRIGGER_NAME, TABLE_NAME, STATUS
      FROM USER_TRIGGERS
      WHERE TRIGGER_NAME LIKE 'TRG_%'
      ORDER BY TABLE_NAME, TRIGGER_NAME
    """)
    for name, table, status in cur.fetchall():
        print(f"  {name:<45} {table:<15} {status}")
    print()

    print("[REPORT] VINCOLI PK/FK")
    print("-" * 70)
    cur.execute("""
      SELECT CONSTRAINT_NAME, TABLE_NAME, CONSTRAINT_TYPE
      FROM USER_CONSTRAINTS
      WHERE CONSTRAINT_TYPE IN ('P','R')
        AND TABLE_NAME NOT LIKE 'SYS_%'
        AND TABLE_NAME NOT LIKE 'AQ_%'
        AND TABLE_NAME NOT LIKE 'HELP%'
        AND TABLE_NAME NOT LIKE 'BIN_%'
        AND TABLE_NAME NOT LIKE 'MVIEW%'
      ORDER BY TABLE_NAME, CONSTRAINT_TYPE
    """)
    for name, table, ctype in cur.fetchall():
        tipo = "PK" if ctype == "P" else "FK"
        print(f"  {tipo} {name:<45} {table}")
    print()
    print("[REPORT] STATO: COMPLETATO")
    cur.close()
    conn.close()

if __name__ == "__main__":
    generate_report(sys.argv[1])
