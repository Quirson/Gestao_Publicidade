"""
CONEXÃO ORACLE PURA - SEM COMPLICAÇÕES
"""

import cx_Oracle

class OracleDatabase:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Conecta DIRETAMENTE à Oracle"""
        try:
            print("🔗 Conectando à Oracle...")

            # CONEXÃO DIRETA E SIMPLES
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XEPDB1")
            self.connection = cx_Oracle.connect(
                user="GESTAO_PUBLICIDADE",
                password="ISCTEM",
                dsn=dsn
            )

            print("🎉 ✅ CONEXÃO ORACLE REAL ESTABELECIDA!")
            return True

        except Exception as e:
            print(f"❌ ERRO DE CONEXÃO: {e}")
            return False

    def execute_query(self, query, params=None, fetch=True):
        """Executa queries REAIS"""
        cursor = None
        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch and cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return (columns, rows)
            else:
                self.connection.commit()
                return True

        except Exception as e:
            print(f"❌ ERRO NA QUERY: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def test_connection(self):
        """Testa conexão"""
        try:
            result = self.execute_query("SELECT '✅ CONECTADO' AS STATUS FROM DUAL")
            return result is not None
        except:
            return False

# Conexão global
db = OracleDatabase()