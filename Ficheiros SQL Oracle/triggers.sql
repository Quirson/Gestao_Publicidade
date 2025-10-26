CREATE TABLE Log_Auditoria_Orcamento (
    Id_log        NUMBER PRIMARY KEY,
    Cod_camp      NUMBER NOT NULL,
    Data_alteracao DATE NOT NULL,
    User_alterou  VARCHAR2(100) NOT NULL,
    Valor_antigo  NUMBER(10, 2),
    Valor_novo    NUMBER(10, 2)
);

-- Sequência para a tabela de Log
CREATE SEQUENCE seq_log_auditoria
  START WITH 1
  INCREMENT BY 1
  NOCACHE;

CREATE OR REPLACE TRIGGER trg_audita_orcamento_campanha
AFTER UPDATE OF Orc_alocado ON Campanha_Dados
FOR EACH ROW
WHEN (NEW.Orc_alocado <> OLD.Orc_alocado) -- Só dispara se o valor realmente mudar
DECLARE
    v_user VARCHAR2(100);
BEGIN
    -- Obtém o usuário da base de dados
    SELECT USER INTO v_user FROM DUAL;

    INSERT INTO Log_Auditoria_Orcamento (
        Id_log,
        Cod_camp,
        Data_alteracao,
        User_alterou,
        Valor_antigo,
        Valor_novo
    )
    VALUES (
        seq_log_auditoria.NEXTVAL,
        :OLD.Cod_camp,
        SYSDATE,
        v_user,
        :OLD.Orc_alocado,
        :NEW.Orc_alocado
    );
END;
/