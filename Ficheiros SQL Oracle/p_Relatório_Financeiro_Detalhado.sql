CREATE OR REPLACE PROCEDURE sp_relatorio_financeiro_anunciante (
    p_nif IN Anunciante_Dados.Num_id_fiscal%TYPE,
    p_data_inicio IN DATE,
    p_data_fim IN DATE,
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
    SELECT c.Cod_camp, c.Titulo, c.Orc_alocado,
           fn_calcular_custo_total_campanha(c.Cod_camp) as Custo_Real,
           (c.Orc_alocado - fn_calcular_custo_total_campanha(c.Cod_camp)) as Lucro_Prejuizo
    FROM Campanha_Dados c
    WHERE c.Num_id_fiscal = p_nif
    AND c.Data_inicio BETWEEN p_data_inicio AND p_data_fim;
END;
/