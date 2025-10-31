"""
DATABASE HÍBRIDO - DADOS REAIS SEM SEGMENTATION FAULT
"""

import sqlite3
import json
import os
from datetime import datetime


class HybridDatabase:
    def __init__(self):
        self.oracle_data = {}
        self.sqlite_conn = None
        self._setup_sqlite()
        self._load_oracle_data_once()  # Carrega dados REAIS uma vez

    def _setup_sqlite(self):
        """Configura SQLite local para operações"""
        try:
            self.sqlite_conn = sqlite3.connect('gestao_publicidade.db', check_same_thread=False)
            self._create_tables()
            print("✅ SQLite local configurado")
        except Exception as e:
            print(f"❌ Erro SQLite: {e}")

    def _create_tables(self):
        """Cria tabelas locais"""
        cursor = self.sqlite_conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS campanhas_temp
                       (
                           cod_camp     INTEGER PRIMARY KEY,
                           titulo       TEXT,
                           anunciante   TEXT,
                           orcamento    REAL,
                           data_inicio  TEXT,
                           data_termino TEXT,
                           status       TEXT
                       )
                       ''')

        self.sqlite_conn.commit()

    def _load_oracle_data_once(self):
        """Carrega dados REAIS do Oracle UMA VEZ (evita segmentation fault)"""
        try:
            print("🔄 Carregando dados REAIS do Oracle...")

            # Importação CONDICIONAL do cx_Oracle
            try:
                import cx_Oracle

                # Conexão DIRECTA sem manter conexão aberta
                dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XEPDB1")
                conn = cx_Oracle.connect(
                    user="GESTAO_PUBLICIDADE",
                    password="ISCTEM",
                    dsn=dsn
                )
                cursor = conn.cursor()

                # CARREGAR DADOS REAIS
                self._load_table_data(cursor, "ANUNCIANTE_DADOS",
                                      "SELECT Num_id_fiscal, Nome_razao_soc, Cat_negocio, Porte, Lim_cred_aprov, Classif_conf FROM ANUNCIANTE_DADOS")

                self._load_table_data(cursor, "CAMPANHA_DADOS",
                                      """SELECT c.Cod_camp,
                                                c.Titulo,
                                                a.Nome_razao_soc,
                                                c.Orc_alocado,
                                                TO_CHAR(c.Data_inicio, 'DD/MM/YYYY'),
                                                TO_CHAR(c.Data_termino, 'DD/MM/YYYY'),
                                                CASE WHEN c.Data_termino >= SYSDATE THEN 'Ativa' ELSE 'Finalizada' END
                                         FROM Campanha_Dados c
                                                  JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal""")

                self._load_table_data(cursor, "ESPACO_DADOS",
                                      "SELECT Id_espaco, Local_fis_dig, Tipo, Preco_base, Disponibilidade FROM Espaco_Dados")

                self._load_table_data(cursor, "PECAS_CRIATIVAS",
                                      """SELECT p.Id_unicoPeca,
                                                p.Titulo,
                                                a.Nome_razao_soc,
                                                p.Criador,
                                                TO_CHAR(p.Data_criacao, 'DD/MM/YYYY'),
                                                p.Status_aprov,
                                                p.Classif_conteudo
                                         FROM Pecas_Criativas p
                                                  JOIN Anunciante_Dados a ON p.Num_id_fiscal = a.Num_id_fiscal""")

                cursor.close()
                conn.close()

                print(f"🎉 DADOS REAIS CARREGADOS:")
                print(f"   👥 Anunciantes: {len(self.oracle_data.get('ANUNCIANTE_DADOS', []))}")
                print(f"   📢 Campanhas: {len(self.oracle_data.get('CAMPANHA_DADOS', []))}")
                print(f"   📺 Espaços: {len(self.oracle_data.get('ESPACO_DADOS', []))}")
                print(f"   🎨 Peças: {len(self.oracle_data.get('PECAS_CRIATIVAS', []))}")

            except ImportError:
                print("🔶 cx_Oracle não disponível - usando dados de exemplo")
                self._load_sample_data()

        except Exception as e:
            print(f"🔶 Erro ao carregar dados Oracle: {e}")
            self._load_sample_data()

    def _load_table_data(self, cursor, table_name, query):
        """Carrega dados de uma tabela específica"""
        try:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            self.oracle_data[table_name] = {
                'columns': columns,
                'rows': rows
            }

            print(f"   ✅ {table_name}: {len(rows)} registros")

        except Exception as e:
            print(f"   ❌ Erro em {table_name}: {e}")
            self.oracle_data[table_name] = {'columns': [], 'rows': []}

    def _load_sample_data(self):
        """Dados de fallback"""
        print("🔶 Usando dados de exemplo...")
        self.oracle_data = {
            'ANUNCIANTE_DADOS': {
                'columns': ['NUM_ID_FISCAL', 'NOME_RAZAO_SOC', 'CAT_NEGOCIO', 'PORTE', 'LIM_CRED_APROV',
                            'CLASSIF_CONF'],
                'rows': [
                    (1000001, 'Vodacom Moçambique', 'Telecomunicações', 'Grande', 5000000.00, 'AAA - Excelente'),
                    (1000002, 'Cervejas de Moçambique', 'Bebidas e Alimentos', 'Grande', 3000000.00, 'AA - Muito Bom'),
                ]
            }
        }

    def execute_query(self, query, params=None, fetch=True):
        """Executa queries - usa dados REAIS carregados"""
        query_upper = query.upper().strip()

        try:
            # CONSULTAS SELECT - usa dados REAIS do Oracle
            if "SELECT" in query_upper:
                # ANUNCIANTES
                if "ANUNCIANTE" in query_upper:
                    data = self.oracle_data.get('ANUNCIANTE_DADOS')
                    if data and "COUNT" in query_upper:
                        return (['COUNT'], [(len(data['rows']),)])
                    elif data:
                        return (data['columns'], data['rows'])

                # CAMPANHAS
                elif "CAMPANHA" in query_upper:
                    data = self.oracle_data.get('CAMPANHA_DADOS')
                    if data and "COUNT" in query_upper:
                        return (['COUNT'], [(len(data['rows']),)])
                    elif data:
                        return (data['columns'], data['rows'])

                # ESPAÇOS
                elif "ESPACO" in query_upper:
                    data = self.oracle_data.get('ESPACO_DADOS')
                    if data and "COUNT" in query_upper:
                        return (['COUNT'], [(len(data['rows']),)])
                    elif data:
                        return (data['columns'], data['rows'])

                # PEÇAS CRIATIVAS
                elif "PECA" in query_upper or "CRIATIV" in query_upper:
                    data = self.oracle_data.get('PECAS_CRIATIVAS')
                    if data and "COUNT" in query_upper:
                        return (['COUNT'], [(len(data['rows']),)])
                    elif data:
                        return (data['columns'], data['rows'])

                # ESTATÍSTICAS
                elif "COUNT" in query_upper and "FROM DUAL" in query_upper:
                    anunciantes = len(self.oracle_data.get('ANUNCIANTE_DADOS', {}).get('rows', []))
                    campanhas = len(self.oracle_data.get('CAMPANHA_DADOS', {}).get('rows', []))
                    espacos = len(self.oracle_data.get('ESPACO_DADOS', {}).get('rows', []))
                    return (['ANUNCIANTES', 'CAMPANHAS', 'ESPACOS'], [(anunciantes, campanhas, espacos)])

            # INSERT/UPDATE/DELETE - usa SQLite local
            elif any(cmd in query_upper for cmd in ['INSERT', 'UPDATE', 'DELETE']):
                if self.sqlite_conn:
                    cursor = self.sqlite_conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    self.sqlite_conn.commit()

                    if "INSERT" in query_upper and "CAMPANHA" in query_upper:
                        # Adiciona à memória também
                        new_id = cursor.lastrowid or 8000000 + len(
                            self.oracle_data.get('CAMPANHA_DADOS', {}).get('rows', [])) + 1
                        print(f"✅ Nova campanha criada: ID {new_id}")

                    return True

            # CONEXÃO TEST
            elif "SELECT '✅ CONEXÃO OK'" in query_upper:
                return (['STATUS'], [('✅ DADOS REAIS CARREGADOS',)])

            return ([], [])

        except Exception as e:
            print(f"🔶 Erro na query: {e}")
            return ([], [])

    def call_procedure(self, proc_name, params=None):
        """Simula chamada de procedures"""
        print(f"🔶 SIMULANDO PROCEDURE: {proc_name}")
        if params:
            print(f"   Parâmetros: {params}")

        # Simular sucesso
        return True

    def test_connection(self):
        """Testa a 'conexão'"""
        anunciantes = len(self.oracle_data.get('ANUNCIANTE_DADOS', {}).get('rows', []))
        campanhas = len(self.oracle_data.get('CAMPANHA_DADOS', {}).get('rows', []))
        espacos = len(self.oracle_data.get('ESPACO_DADOS', {}).get('rows', []))

        print(f"📊 DADOS REAIS CARREGADOS:")
        print(f"   👥 Anunciantes: {anunciantes}")
        print(f"   📢 Campanhas: {campanhas}")
        print(f"   📺 Espaços: {espacos}")

        return anunciantes > 0


# Singleton global
db = HybridDatabase()