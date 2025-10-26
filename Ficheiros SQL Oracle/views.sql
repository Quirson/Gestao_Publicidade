CREATE OR REPLACE VIEW v_campanhas_ativas AS
SELECT
    c.Cod_camp,
    c.Titulo AS Campanha_Titulo,
    c.Objectivo,
    c.Orc_alocado,
    c.Data_inicio,
    c.Data_termino,
    a.Nome_razao_soc AS Anunciante,
    p.Titulo AS Peca_Titulo,
    p.Descricao AS Peca_Descricao,
    -- Concatena todos os espaços publicitários numa só string
    (SELECT LISTAGG(e.Local_fis_dig, '; ') WITHIN GROUP (ORDER BY e.Local_fis_dig)
     FROM Campanha_Espaco ce
     JOIN Espaco_Dados e ON ce.Id_espaco = e.Id_espaco
     WHERE ce.Cod_camp = c.Cod_camp) AS Espacos_Utilizados
FROM
    Campanha_Dados c
JOIN
    Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
LEFT JOIN
    Pecas_Criativas p ON c.Id_unicoPeca = p.Id_unicoPeca
WHERE
    c.Data_termino >= SYSDATE; -- Mostra apenas campanhas ativas ou futuras