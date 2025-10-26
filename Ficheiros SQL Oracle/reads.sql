-- Procedimento para buscar UM anunciante
CREATE OR REPLACE PROCEDURE sp_get_anunciante_detalhes (
    p_nif         IN  Anunciante_Dados.Num_id_fiscal%TYPE,
    p_cursor      OUT SYS_REFCURSOR -- <--- O CURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
        SELECT * FROM Anunciante_Dados
        WHERE Num_id_fiscal = p_nif;
END;
/

-- Procedimento para buscar TODOS os anunciantes
CREATE OR REPLACE PROCEDURE sp_get_todos_anunciantes (
    p_cursor      OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
        SELECT Num_id_fiscal, Nome_razao_soc, Cat_negocio, Porte, Contactos
        FROM Anunciante_Dados
        ORDER BY Nome_razao_soc;
END;
/