#!/usr/bin/env python3

print("🧪 TESTANDO CONEXÃO ORACLE...")

try:
    from database_oracle import db

    if db.connection:
        print("🎉 CONEXÃO BEM-SUCEDIDA!")

        # Testar query real
        result = db.execute_query("SELECT * FROM ANUNCIANTE_DADOS WHERE ROWNUM <= 3")
        if result:
            columns, rows = result
            print(f"📋 Colunas: {columns}")
            print("📊 Dados reais:")
            for row in rows:
                print(f"   👤 {row[1]} (NIF: {row[0]})")
    else:
        print("❌ FALHA NA CONEXÃO")

except Exception as e:
    print(f"💥 ERRO: {e}")