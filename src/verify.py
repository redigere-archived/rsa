import sys
import oracledb

password = sys.argv[1]

conn = oracledb.connect(user="system", password=password, dsn="localhost:1521/FREEPDB1")
cur = conn.cursor()

print("[RECORD] INIZIO VERIFICA DATI")
print()

tables = [
    "PERSONA","PERSONALE","PARENTE","TUTORE","OPERATORE","CONTRATTO",
    "MEDICO","REPARTO","CAMERA","RESIDENTE","MALATTIA","FARMACO",
    "TRATTAMENTO","SOFFRE","ASSUME","PAI","NECESSITA","AZIENDA_ESTERNA",
    "DITTA","FORNITORE","DITTA_PULIZIA","DITTA_RISTORANTE",
    "FORNISCE","PULISCE","DOCUMENTO","ENTE","PRENOTAZIONE",
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
        print(f"[RECORD] {t:<30} VUOTA")
    else:
        print(f"[RECORD] {t:<30} {count:>4} record")

print()
print(f"[RECORD] Tabelle: {len(tables)} | Record totali: {total} | Vuote: {len(empty)}")
if empty:
    print(f"[RECORD] STATO: ERRORE ({', '.join(empty)} vuote)")
    sys.exit(1)
print("[RECORD] STATO: OK")

cur.close()
conn.close()
