CREATE OR REPLACE PROCEDURE sp_update_anunciante_contacto (
    p_nif           IN Anunciante_Dados.Num_id_fiscal%TYPE,
    p_novo_contacto IN Anunciante_Dados.Contactos%TYPE,
    p_novo_rep      IN Anunciante_Dados.Rep_legal%TYPE
)
IS
BEGIN
    UPDATE Anunciante_Dados
    SET
        Contactos = p_novo_contacto,
        Rep_legal = p_novo_rep
    WHERE
        Num_id_fiscal = p_nif;

    COMMIT;
END;
/