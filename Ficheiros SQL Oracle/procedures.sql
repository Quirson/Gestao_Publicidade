CREATE OR REPLACE PROCEDURE sp_criar_anunciante (
    p_nome_razao_soc   IN Anunciante_Dados.Nome_razao_soc%TYPE,
    p_cat_negocio      IN Anunciante_Dados.Cat_negocio%TYPE,
    p_porte            IN Anunciante_Dados.Porte%TYPE,
    p_endereco         IN Anunciante_Dados.Endereco%TYPE,
    p_contactos        IN Anunciante_Dados.Contactos%TYPE,
    p_rep_legal        IN Anunciante_Dados.Rep_legal%TYPE,
    p_lim_cred_aprov   IN Anunciante_Dados.Lim_cred_aprov%TYPE,
    p_classif_conf     IN Anunciante_Dados.Classif_conf%TYPE
)
IS
BEGIN
    INSERT INTO Anunciante_Dados (
        Num_id_fiscal,
        Nome_razao_soc,
        Cat_negocio,
        Porte,
        Endereco,
        Contactos,
        Rep_legal,
        Pref_com, -- Assumindo um valor default
        Lim_cred_aprov,
        Classif_conf
    )
    VALUES (
        seq_anunciante.NEXTVAL, -- <--- USA A SEQUÊNCIA AQUI
        p_nome_razao_soc,
        p_cat_negocio,
        p_porte,
        p_endereco,
        p_contactos,
        p_rep_legal,
        'Email', -- Valor default
        p_lim_cred_aprov,
        p_classif_conf
    );
    COMMIT;
END;
/