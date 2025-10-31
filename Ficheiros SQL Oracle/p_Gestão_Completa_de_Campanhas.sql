-CREATE OR REPLACE PROCEDURE sp_gestao_campanha_completa (
    p_operacao IN VARCHAR2, -- 'INSERT', 'UPDATE', 'DELETE'
    p_cod_camp IN Campanha_Dados.Cod_camp%TYPE DEFAULT NULL,
    p_dados_campanha IN SYS_REFCURSOR DEFAULT NULL
)
IS
    v_count NUMBER;
BEGIN
    IF p_operacao = 'INSERT' THEN
        -- Usar a procedure que já criamos
        sp_inserir_campanha_completa(...);

    ELSIF p_operacao = 'UPDATE' THEN
        -- Atualizar campanha com validações
        UPDATE Campanha_Dados SET ... WHERE Cod_camp = p_cod_camp;

    ELSIF p_operacao = 'DELETE' THEN
        -- Verificar dependências antes de apagar
        SELECT COUNT(*) INTO v_count FROM Pecas_Criativas WHERE Cod_camp = p_cod_camp;
        IF v_count > 0 THEN
            RAISE_APPLICATION_ERROR(-20001, 'Campanha possui peças criativas associadas');
        END IF;

        DELETE FROM Campanha_Dados WHERE Cod_camp = p_cod_camp;
    END IF;

    COMMIT;
END;
/