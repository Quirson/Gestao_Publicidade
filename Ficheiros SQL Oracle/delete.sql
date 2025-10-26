CREATE OR REPLACE PROCEDURE sp_delete_anunciante (
    p_nif IN Anunciante_Dados.Num_id_fiscal%TYPE
)
IS
BEGIN
    -- ATENÇÃO: Isto vai falhar se o anunciante tiver campanhas (foreign key constraint).
    -- Para um trabalho escolar, podes primeiro apagar as relações
    -- ou configurar "ON DELETE CASCADE" nas tuas chaves estrangeiras.
    -- Vamos assumir que as dependências são tratadas ou não existem.

    -- Exemplo de como tratar dependências (ex: Anunciante_Agencia)
    DELETE FROM Anunciante_Agencia WHERE Num_id_fiscal = p_nif;
    -- Terias de fazer o mesmo para Campanha_Dados, Pecas_Criativas, etc.

    -- Finalmente, apagar o anunciante
    DELETE FROM Anunciante_Dados
    WHERE Num_id_fiscal = p_nif;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        -- Adicionar tratamento de erro (ex: logar o erro)
        ROLLBACK;
        RAISE;
END;
/