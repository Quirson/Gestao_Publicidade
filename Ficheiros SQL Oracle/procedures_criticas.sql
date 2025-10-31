-- 🚀 PROCEDURES CRÍTICAS PARA O SISTEMA

-- 1. PROCEDURE: GESTÃO COMPLETA DE CAMPANHAS
CREATE OR REPLACE PROCEDURE sp_inserir_campanha_completa (
    p_num_id_fiscal    IN Campanha_Dados.Num_id_fiscal%TYPE,
    p_titulo          IN Campanha_Dados.Titulo%TYPE,
    p_objectivo       IN Campanha_Dados.Objectivo%TYPE,
    p_pub_alvo        IN Campanha_Dados.Pub_alvo%TYPE,
    p_orc_alocado     IN Campanha_Dados.Orc_alocado%TYPE,
    p_data_inicio     IN VARCHAR2, -- Aceita string para facilitar
    p_data_termino    IN VARCHAR2,
    p_espacos_ids     IN VARCHAR2 DEFAULT NULL,
    p_publico_ids     IN VARCHAR2 DEFAULT NULL,
    p_canais          IN VARCHAR2 DEFAULT NULL
)
IS
    v_cod_camp NUMBER;
    v_limite_cred NUMBER;
    v_orc_total NUMBER := 0;
BEGIN
    -- 1. VERIFICAR LIMITE DE CRÉDITO
    BEGIN
        SELECT Lim_cred_aprov INTO v_limite_cred
        FROM Anunciante_Dados
        WHERE Num_id_fiscal = p_num_id_fiscal;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20001, 'Anunciante não encontrado: ' || p_num_id_fiscal);
    END;

    IF p_orc_alocado > v_limite_cred THEN
        RAISE_APPLICATION_ERROR(-20002, 'Orçamento excede limite de crédito. Limite: ' || v_limite_cred);
    END IF;

    -- 2. GERAR NOVO ID
    SELECT NVL(MAX(Cod_camp), 8000000) + 1 INTO v_cod_camp FROM Campanha_Dados;

    -- 3. INSERIR CAMPANHA
    INSERT INTO Campanha_Dados (
        Cod_camp, Num_id_fiscal, Titulo, Objectivo, Pub_alvo,
        Orc_alocado, Data_inicio, Data_termino
    ) VALUES (
        v_cod_camp,
p_num_id_fiscal, p_titulo, p_objectivo, p_pub_alvo,
        p_orc_alocado, TO_DATE(p_data_inicio, 'DD/MM/YYYY'), TO_DATE(p_data_termino, 'DD/MM/YYYY')
    );

    -- 4. ASSOCIAR ESPAÇOS (se fornecidos)
    IF p_espacos_ids IS NOT NULL THEN
        FOR i IN (SELECT TRIM(REGEXP_SUBSTR(p_espacos_ids, '[^,]+', 1, LEVEL)) AS espaco_id
                  FROM DUAL
                  CONNECT BY REGEXP_SUBSTR(p_espacos_ids, '[^,]+', 1, LEVEL) IS NOT NULL)
        LOOP
            INSERT INTO Campanha_Espaco (Cod_camp, Id_espaco)
            VALUES (v_cod_camp, i.espaco_id);
        END LOOP;
    END IF;
    -- 5. ASSOCIAR PÚBLICO-ALVO (se fornecido)
    IF p_publico_ids IS NOT NULL THEN
        FOR i IN (SELECT TRIM(REGEXP_SUBSTR(p_publico_ids, '[^,]+', 1, LEVEL)) AS publico_id
                  FROM DUAL
                  CONNECT BY REGEXP_SUBSTR(p_publico_ids, '[^,]+', 1, LEVEL) IS NOT NULL)
        LOOP
            INSERT INTO Campanha_PublicoAlvo (Cod_camp, Id_publicoAlvo)
            VALUES (v_cod_camp, i.publico_id);
        END LOOP;
    END IF;

    -- 6. ASSOCIAR CANAIS (se fornecidos)
    IF p_canais IS NOT NULL THEN
        FOR i IN (SELECT TRIM(REGEXP_SUBSTR(p_canais, '[^,]+', 1, LEVEL)) AS canal
                  FROM DUAL
                  CONNECT BY REGEXP_SUBSTR(p_canais, '[^,]+', 1, LEVEL) IS NOT NULL)
        LOOP
            INSERT INTO Campanha_Canal (Cod_camp, Canais_util)
            VALUES (v_cod_camp, i.canal);
        END LOOP;
    END IF;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END sp_inserir_campanha_completa;
/

-- 2. FUNCTION: CALCULAR CUSTO TOTAL COM DESCONTO
CREATE OR REPLACE FUNCTION fn_calcular_custo_total_campanha (
    p_cod_camp IN Campanha_Dados.Cod_camp%TYPE
) RETURN NUMBER
IS
    v_custo_base NUMBER := 0;
    v_desconto NUMBER := 0;
    v_cod_pagamento NUMBER;
    v_cod_promocao NUMBER;
BEGIN
    -- Buscar custo base dos espaços
    SELECT SUM(e.Preco_base)
    INTO v_custo_base
    FROM Campanha_Espaco ce
    JOIN Espaco_Dados e ON ce.Id_espaco = e.Id_espaco
    WHERE ce.Cod_camp = p_cod_camp;

    -- Buscar desconto da promoção
    BEGIN
        SELECT cd.Cod_pagamento, p.Cod_promocao
        INTO v_cod_pagamento, v_cod_promocao
        FROM Campanha_Dados cd
        LEFT JOIN Pagamentos p ON cd.Cod_pagamento = p.Cod_pagamento
        WHERE cd.Cod_camp = p_cod_camp;

        IF v_cod_promocao IS NOT NULL THEN
            SELECT Desc_volume INTO v_desconto
            FROM Promocoes
            WHERE Cod_promocao = v_cod_promocao;
        END IF;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_desconto := 0;
    END;

    -- Aplicar desconto
    RETURN NVL(v_custo_base, 0) * (1 - NVL(v_desconto, 0) / 100);

EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END fn_calcular_custo_total_campanha;
/

-- 3. PROCEDURE: RELATÓRIO FINANCEIRO
CREATE OR REPLACE PROCEDURE sp_relatorio_financeiro_anunciante (
    p_nif IN Anunciante_Dados.Num_id_fiscal%TYPE,
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
    SELECT
        c.Cod_camp,
        c.Titulo AS Campanha,
        c.Orc_alocado AS Orcamento,
        fn_calcular_custo_total_campanha(c.Cod_camp) AS Custo_Real,
        (c.Orc_alocado - fn_calcular_custo_total_campanha(c.Cod_camp)) AS Resultado,
        CASE
            WHEN fn_calcular_custo_total_campanha(c.Cod_camp) = 0 THEN 0
            ELSE ROUND(((c.Orc_alocado - fn_calcular_custo_total_campanha(c.Cod_camp)) / c.Orc_alocado) * 100, 2)
        END AS Performance_Perc
    FROM Campanha_Dados c
    WHERE c.Num_id_fiscal = p_nif
    ORDER BY c.Data_inicio DESC;
END sp_relatorio_financeiro_anunciante;
/

-- 4. PROCEDURE: APROVAR/REJEITAR PEÇA
CREATE OR REPLACE PROCEDURE sp_aprovar_rejeitar_peca (
    p_id_peca IN Pecas_Criativas.Id_unicoPeca%TYPE,
    p_novo_status IN Pecas_Criativas.Status_aprov%TYPE,
    p_justificativa IN VARCHAR2 DEFAULT NULL
)
IS
    v_status_atual VARCHAR2(20);
BEGIN
    -- Verificar se peça existe
    SELECT Status_aprov INTO v_status_atual
    FROM Pecas_Criativas
    WHERE Id_unicoPeca = p_id_peca;

    -- Atualizar status
    UPDATE Pecas_Criativas
    SET Status_aprov = p_novo_status
    WHERE Id_unicoPeca = p_id_peca;

    -- Registrar no log (se tivéssemos tabela de log)
    -- INSERT INTO Log_Aprovacao_Pecas ...

    COMMIT;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20003, 'Peça criativa não encontrada: ' || p_id_peca);
END sp_aprovar_rejeitar_peca;
/

-- 5. PROCEDURE: BUSCAR DETALHES COMPLETOS CAMPANHA
CREATE OR REPLACE PROCEDURE sp_get_detalhes_campanha_completa (
    p_cod_camp IN Campanha_Dados.Cod_camp%TYPE,
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
    SELECT
        c.*,
        a.Nome_razao_soc AS Anunciante_Nome,
        (SELECT LISTAGG(e.Local_fis_dig, '; ') WITHIN GROUP (ORDER BY e.Local_fis_dig)
         FROM Campanha_Espaco ce
         JOIN Espaco_Dados e ON ce.Id_espaco = e.Id_espaco
         WHERE ce.Cod_camp = c.Cod_camp) AS Espacos,
        (SELECT LISTAGG(pa.Seg_demograf, ' | ') WITHIN GROUP (ORDER BY pa.Id_publicoAlvo)
         FROM Campanha_PublicoAlvo cpa
         JOIN Publico_Alvo pa ON cpa.Id_publicoAlvo = pa.Id_publicoAlvo
         WHERE cpa.Cod_camp = c.Cod_camp) AS Publicos_Alvo,
        fn_calcular_custo_total_campanha(c.Cod_camp) AS Custo_Total
    FROM Campanha_Dados c
    JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
    WHERE c.Cod_camp = p_cod_camp;
END sp_get_detalhes_campanha_completa;
/

-- 6. PROCEDURE: ESTATÍSTICAS DO SISTEMA
CREATE OR REPLACE PROCEDURE sp_estatisticas_sistema (
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
    WITH stats AS (
        SELECT
            (SELECT COUNT(*) FROM Anunciante_Dados) as total_anunciantes,
            (SELECT COUNT(*) FROM Campanha_Dados) as total_campanhas,
            (SELECT COUNT(*) FROM Campanha_Dados WHERE Data_termino >= SYSDATE) as campanhas_ativas,
            (SELECT COUNT(*) FROM Espaco_Dados) as total_espacos,
            (SELECT COUNT(*) FROM Espaco_Dados WHERE Disponibilidade = 'Disponível') as espacos_disponiveis,
            (SELECT SUM(Orc_alocado) FROM Campanha_Dados WHERE Data_termino >= SYSDATE) as orcamento_total_ativas
        FROM DUAL
    )
    SELECT * FROM stats;
END sp_estatisticas_sistema;
/

COMMIT;
/