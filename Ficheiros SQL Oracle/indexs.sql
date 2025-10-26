-- Índices para Chaves Estrangeiras (FKs)
CREATE INDEX idx_campanha_nif ON Campanha_Dados(Num_id_fiscal);
CREATE INDEX idx_campanha_peca ON Campanha_Dados(Id_unicoPeca);
CREATE INDEX idx_campanha_pag ON Campanha_Dados(Cod_pagamento);
CREATE INDEX idx_peca_nif ON Pecas_Criativas(Num_id_fiscal);
CREATE INDEX idx_peca_camp ON Pecas_Criativas(Cod_camp);
CREATE INDEX idx_pag_modalidade ON Pagamentos(Cod_modalidade);
CREATE INDEX idx_pag_promocao ON Pagamentos(Cod_promocao);
CREATE INDEX idx_camp_esp_camp ON Campanha_Espaco(Cod_camp);
CREATE INDEX idx_camp_esp_esp ON Campanha_Espaco(Id_espaco);
CREATE INDEX idx_camp_pub_camp ON Campanha_PublicoAlvo(Cod_camp);
CREATE INDEX idx_camp_pub_pub ON Campanha_PublicoAlvo(Id_publicoAlvo);

-- Índice para pesquisa (Ex: pesquisar anunciante por nome)
CREATE INDEX idx_anunciante_nome ON Anunciante_Dados(Nome_razao_soc);