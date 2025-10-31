CREATE OR REPLACE FUNCTION fn_calcular_performance_campanha (
    p_cod_camp IN Campanha_Dados.Cod_camp%TYPE
) RETURN NUMBER
IS
    v_orcamento NUMBER;
    v_custo_real NUMBER;
    v_performance NUMBER;
BEGIN
    SELECT Orc_alocado INTO v_orcamento
    FROM Campanha_Dados WHERE Cod_camp = p_cod_camp;

    v_custo_real := fn_calcular_custo_total_campanha(p_cod_camp);

    IF v_orcamento > 0 THEN
        v_performance := ((v_orcamento - v_custo_real) / v_orcamento) * 100;
    ELSE
        v_performance := 0;
    END IF;

    RETURN ROUND(v_performance, 2);
END;
/