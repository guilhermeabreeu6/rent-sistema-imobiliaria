#!/usr/bin/env python3
# Script de teste para verificar conexão e dados do banco

from db.conexao import obter_conexao

def testar_conexao():
    print("🔍 Testando conexão com o banco de dados...")
    try:
        conexao = obter_conexao()
        if conexao:
            print("✅ Conexão bem-sucedida!")
            
            cursor = conexao.cursor(dictionary=True)
            
            # Verificar se a tabela existe
            print("\n📋 Verificando estrutura da tabela...")
            cursor.execute("DESCRIBE clientes")
            estrutura = cursor.fetchall()
            print("Estrutura da tabela 'clientes':")
            for coluna in estrutura:
                print(f"  - {coluna}")
            
            # Contar registros
            print("\n📊 Contando registros...")
            cursor.execute("SELECT COUNT(*) as total FROM clientes")
            resultado = cursor.fetchone()
            total_clientes = resultado['total']
            print(f"Total de clientes: {total_clientes}")
            
            # Mostrar todos os clientes
            if total_clientes > 0:
                print("\n👥 Lista de clientes:")
                cursor.execute("SELECT * FROM clientes")
                clientes = cursor.fetchall()
                for i, cliente in enumerate(clientes, 1):
                    print(f"  {i}. {cliente}")
            else:
                print("\n⚠️  Nenhum cliente encontrado no banco de dados!")
                print("💡 Tente cadastrar um cliente primeiro através da aplicação web.")
            
            cursor.close()
            conexao.close()
            
        else:
            print("❌ Falha na conexão!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_conexao()