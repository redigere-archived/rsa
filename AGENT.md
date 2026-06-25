# RSA - Sistema Gestionale Sanitario

## Ruolo

Senior Database Architect e sviluppatore PL/SQL specializzato in Oracle Database XE.

## Obiettivo

Generare e mantenere lo script SQL per limplementazione del DDL e del DML di un sistema gestionale sanitario per Residenza Sanitaria Assistenziale.

## Struttura del Database

Il database e composto da 33 tabelle organizzate in 5 macro aree:

- Entita Anagrafiche Centrali con gerarchia PERSONA
- Struttura, Reparti e Contratti
- Entita Esterne, Fornitori e Servizi
- Clinica, Trattamenti e Sanita
- Prenotazioni, Visite e Turni

## Dipendenze

Le tabelle sono ordinate in modo gerarchico per prevenire errori di Parent key not found. Le tabelle madri precedono sempre le tabelle figlie e le tabelle di relazione molti a molti.

## Convenzioni Oracle

Ogni tabella usa VARCHAR2 al posto di VARCHAR. Le chiavi surrogate numeriche usano NUMBER. I vincoli PK e FK sono definiti con CONSTRAINT esplicito. Le chiavi composte sono definite a fondo tabella.

## Script SQL

Lo script DDL contiene i comandi DROP TABLE CASCADE CONSTRAINTS in ordine inverso seguiti dai CREATE TABLE in ordine diretto. Lo script DML contiene tra i 3 e i 5 record di test per tabella con dati clinici italiani realistici. Le date usano la funzione TO_DATE. Il blocco DML si chiude con COMMIT.

## CI CD

Il workflow GitHub Actions avvia Oracle XE tramite Docker, esegue gli script SQL e verifica che tutte le tabelle siano popolate.
