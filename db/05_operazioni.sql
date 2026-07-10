CREATE OR REPLACE FUNCTION AMMETTI_RESIDENTE(
    p_cf_persona IN VARCHAR2,
    p_nome IN VARCHAR2,
    p_cognome IN VARCHAR2,
    p_data_nascita IN DATE,
    p_numero_camera IN NUMBER
) RETURN NUMBER AS
    v_count NUMBER;
    v_letti_totali NUMBER;
    v_occupati NUMBER;
    v_disponibilita NUMBER;
BEGIN
    SELECT NVL(SUM(LETTI_TOTALI), 0) INTO v_letti_totali FROM CAMERA;
    SELECT COUNT(*) INTO v_occupati FROM RESIDENTE;
    v_disponibilita := v_letti_totali - v_occupati;
    IF v_disponibilita <= 0 THEN
        RETURN 0;
    END IF;
    SELECT COUNT(*) INTO v_count FROM PERSONA WHERE CODICE_FISCALE = p_cf_persona;
    IF v_count = 0 THEN
        INSERT INTO PERSONA (CODICE_FISCALE, NOME, COGNOME, DATA_NASCITA)
        VALUES (p_cf_persona, p_nome, p_cognome, p_data_nascita);
    END IF;
    INSERT INTO RESIDENTE (CODICE_FISCALE_RESIDENTE, NUMERO_CAMERA)
    VALUES (p_cf_persona, p_numero_camera);
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/

CREATE OR REPLACE FUNCTION CONTROLLO_RESIDENTE(
    p_cf_residente IN VARCHAR2
) RETURN NUMBER AS
    v_ammesso NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_ammesso FROM RESIDENTE WHERE CODICE_FISCALE_RESIDENTE = p_cf_residente;
    IF v_ammesso > 0 THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
END;
/

CREATE OR REPLACE FUNCTION ASSUMI_MEDICO(
    p_cf IN VARCHAR2, 
    p_nome IN VARCHAR2, 
    p_cognome IN VARCHAR2, 
    p_data_nascita IN DATE,
    p_cod_contratto IN NUMBER, 
    p_tipo_contratto IN VARCHAR2, 
    p_paga_oraria IN NUMBER, 
    p_tassa IN NUMBER
) RETURN NUMBER AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM PERSONA WHERE CODICE_FISCALE = p_cf;
    IF v_count = 0 THEN
        INSERT INTO PERSONA (CODICE_FISCALE, NOME, COGNOME, DATA_NASCITA)
        VALUES (p_cf, p_nome, p_cognome, p_data_nascita);
    END IF;
    INSERT INTO PERSONALE (CODICE_FISCALE) VALUES (p_cf);
    INSERT INTO CONTRATTO (CODICE_CONTRATTO, TIPO_CONTRATTO, PAGA_ORARIA, TASSA_DETRATTA, CODICE_FISCALE_PERSONALE)
    VALUES (p_cod_contratto, p_tipo_contratto, p_paga_oraria, p_tassa, p_cf);
    INSERT INTO MEDICO (CODICE_FISCALE, CODICE_CONTRATTO) VALUES (p_cf, p_cod_contratto);
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/

CREATE OR REPLACE FUNCTION REGISTRA_CONSULENZA(
    p_cod_consulenza IN NUMBER, 
    p_data IN DATE, 
    p_note IN CLOB,
    p_cf_medico IN VARCHAR2, 
    p_cf_residente IN VARCHAR2
) RETURN NUMBER AS
BEGIN
    INSERT INTO CONSULENZA (CODICE_CONSULENZA, DATA_CONSULENZA, NOTE_CONSULENZA)
    VALUES (p_cod_consulenza, p_data, p_note);
    INSERT INTO EFFETTUA (CODICE_CONSULENZA, CODICE_FISCALE_MEDICO)
    VALUES (p_cod_consulenza, p_cf_medico);
    INSERT INTO RICEVE (CODICE_FISCALE_RESIDENTE, CODICE_CONSULENZA)
    VALUES (p_cf_residente, p_cod_consulenza);
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/

CREATE OR REPLACE FUNCTION SPOSTA_RESIDENTE(
    p_cf_residente IN VARCHAR2,
    p_nuova_camera IN NUMBER
) RETURN NUMBER AS
BEGIN
    UPDATE RESIDENTE
    SET NUMERO_CAMERA = p_nuova_camera
    WHERE CODICE_FISCALE_RESIDENTE = p_cf_residente;
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/

CREATE OR REPLACE FUNCTION REGISTRA_INGRESSO_VISITA(
    p_cf_parente IN VARCHAR2,
    p_cf_residente IN VARCHAR2
) RETURN NUMBER AS
    v_esiste_residente NUMBER;
BEGIN
    v_esiste_residente := CONTROLLO_RESIDENTE(p_cf_residente);
    IF v_esiste_residente = 0 THEN
        RETURN 0;
    END IF;
    INSERT INTO VISITA (CODICE_FISCALE_PARENTE, GIORNO_VISITA, ORA_INGRESSO, ORA_USCITA, CODICE_FISCALE_RESIDENTE)
    VALUES (p_cf_parente, TRUNC(SYSDATE), TO_CHAR(SYSDATE, 'HH24:MI'), NULL, p_cf_residente);
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/

CREATE OR REPLACE FUNCTION REGISTRA_USCITA_VISITA(
    p_cf_parente IN VARCHAR2,
    p_cf_residente IN VARCHAR2
) RETURN NUMBER AS
BEGIN
    UPDATE VISITA
    SET ORA_USCITA = TO_CHAR(SYSDATE, 'HH24:MI')
    WHERE CODICE_FISCALE_PARENTE = p_cf_parente
      AND GIORNO_VISITA = TRUNC(SYSDATE)
      AND CODICE_FISCALE_RESIDENTE = p_cf_residente
      AND ORA_USCITA IS NULL;
    COMMIT;
    RETURN 1;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RETURN 0;
END;
/
