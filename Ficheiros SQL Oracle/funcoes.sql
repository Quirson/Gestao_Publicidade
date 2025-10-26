CREATE OR REPLACE FUNCTION fn_calcular_custo_base_campanha (
    p_cod_camp IN Campanha_Dados.Cod_camp%TYPE
)
RETURN NUMBER
IS
    v_custo_total NUMBER(12, 2) := 0;
BEGIN
    -- Soma o Preco_base de todos os Espaços associados a esta campanha
    SELECT SUM(e.Preco_base)
    INTO v_custo_total
    FROM Campanha_Espaco ce
    JOIN Espaco_Dados e ON ce.Id_espaco = e.Id_espaco
    WHERE ce.Cod_camp = p_cod_camp;

    -- (Poderias expandir isto para buscar o Cod_pagamento da campanha,
    -- ir à tabela Pagamentos, buscar a Promocao e aplicar o desconto)

    RETURN NVL(v_custo_total, 0); -- Retorna 0 se for nulo
END;
/