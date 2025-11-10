#!/usr/bin/env python3
# Script para configurar o banco de dados completo

from db.conexao import obter_conexao

def criar_tabela_imoveis():
    """Cria a tabela de imóveis"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        print("🏠 Criando tabela de imóveis...")
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'invistta' 
            AND TABLE_NAME = 'imoveis'
        """)
        
        tabela_existe = cursor.fetchone()[0] > 0
        
        if not tabela_existe:
            cursor.execute("""
                CREATE TABLE imoveis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tipo VARCHAR(50) NOT NULL,
                    endereco VARCHAR(200) NOT NULL,
                    valor DECIMAL(12,2) NOT NULL,
                    status ENUM('disponível', 'vendido', 'alugado') DEFAULT 'disponível',
                    corretor_id INT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (corretor_id) REFERENCES corretores(id) ON DELETE SET NULL
                )
            """)
            conexao.commit()
            print("✅ Tabela 'imoveis' criada com sucesso!")
        else:
            print("ℹ️ Tabela 'imoveis' já existe")
        
        cursor.close()
        conexao.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela de imóveis: {e}")

def criar_tabela_corretores():
    """Cria a tabela de corretores se não existir"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        print("👨‍💼 Verificando tabela de corretores...")
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'invistta' 
            AND TABLE_NAME = 'corretores'
        """)
        
        tabela_existe = cursor.fetchone()[0] > 0
        
        if not tabela_existe:
            cursor.execute("""
                CREATE TABLE corretores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    creci VARCHAR(20) UNIQUE,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conexao.commit()
            print("✅ Tabela 'corretores' criada com sucesso!")
            
            # Inserir corretor padrão
            cursor.execute("""
                INSERT INTO corretores (nome, email, telefone, creci) 
                VALUES ('Corretor Padrão', 'corretor@invistta.com', '63 99999-0000', 'CRECI-12345')
            """)
            conexao.commit()
            print("✅ Corretor padrão inserido!")
            
        else:
            print("ℹ️ Tabela 'corretores' já existe")
        
        cursor.close()
        conexao.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela de corretores: {e}")

def criar_tabela_interesses():
    """Cria a tabela de interesses se não existir"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        print("💙 Criando tabela de interesses...")
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'invistta' 
            AND TABLE_NAME = 'interesses'
        """)
        
        tabela_existe = cursor.fetchone()[0] > 0
        
        if not tabela_existe:
            cursor.execute("""
                CREATE TABLE interesses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    imovel_id INT NOT NULL,
                    status_interesse ENUM('Ativo', 'Pendente', 'Finalizado', 'Cancelado') DEFAULT 'Ativo',
                    data_interesse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                    FOREIGN KEY (imovel_id) REFERENCES imoveis(id) ON DELETE CASCADE
                )
            """)
            conexao.commit()
            print("✅ Tabela 'interesses' criada com sucesso!")
        else:
            print("ℹ️ Tabela 'interesses' já existe")
        
        cursor.close()
        conexao.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela de interesses: {e}")

def adicionar_indices_unicos():
    """Adiciona índices únicos para email e telefone na tabela clientes"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        print("🔧 Adicionando restrições únicas ao banco de dados...")
        
        # Verificar se já existem índices únicos
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.TABLE_CONSTRAINTS 
            WHERE TABLE_SCHEMA = 'invistta' 
            AND TABLE_NAME = 'clientes' 
            AND CONSTRAINT_TYPE = 'UNIQUE'
        """)
        
        indices_existentes = cursor.fetchall()
        print(f"Índices únicos existentes: {indices_existentes}")
        
        # Adicionar índice único para email
        try:
            cursor.execute("ALTER TABLE clientes ADD CONSTRAINT uk_cliente_email UNIQUE (email)")
            print("✅ Índice único para email adicionado!")
        except Exception as e:
            if "Duplicate entry" in str(e):
                print("❌ ERRO: Existem emails duplicados no banco! É necessário limpar primeiro.")
                # Mostrar emails duplicados
                cursor.execute("""
                    SELECT email, COUNT(*) as qtd 
                    FROM clientes 
                    GROUP BY email 
                    HAVING COUNT(*) > 1
                """)
                duplicados = cursor.fetchall()
                print("📋 Emails duplicados encontrados:")
                for email, qtd in duplicados:
                    print(f"  - {email}: {qtd} registros")
            elif "already exists" in str(e) or "Duplicate key" in str(e):
                print("ℹ️ Índice único para email já existe")
            else:
                print(f"❌ Erro ao adicionar índice único para email: {e}")
        
        # Adicionar índice único para telefone (permitindo NULL)
        try:
            # Remover telefones vazios primeiro
            cursor.execute("UPDATE clientes SET telefone = NULL WHERE telefone = '' OR telefone IS NULL")
            
            cursor.execute("ALTER TABLE clientes ADD CONSTRAINT uk_cliente_telefone UNIQUE (telefone)")
            print("✅ Índice único para telefone adicionado!")
        except Exception as e:
            if "Duplicate entry" in str(e):
                print("❌ ERRO: Existem telefones duplicados no banco! É necessário limpar primeiro.")
                # Mostrar telefones duplicados
                cursor.execute("""
                    SELECT telefone, COUNT(*) as qtd 
                    FROM clientes 
                    WHERE telefone IS NOT NULL AND telefone != ''
                    GROUP BY telefone 
                    HAVING COUNT(*) > 1
                """)
                duplicados = cursor.fetchall()
                print("📋 Telefones duplicados encontrados:")
                for telefone, qtd in duplicados:
                    print(f"  - {telefone}: {qtd} registros")
            elif "already exists" in str(e) or "Duplicate key" in str(e):
                print("ℹ️ Índice único para telefone já existe")
            else:
                print(f"❌ Erro ao adicionar índice único para telefone: {e}")
        
        conexao.commit()
        cursor.close()
        conexao.close()
        
        print("\n🎉 Processo concluído!")
        print("💡 Agora o banco de dados impede automaticamente dados duplicados!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def limpar_duplicatas():
    """Remove registros duplicados mantendo apenas o mais recente"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        
        print("🧹 Limpando duplicatas...")
        
        # Remover duplicatas de email (manter o mais recente)
        cursor.execute("""
            DELETE c1 FROM clientes c1
            INNER JOIN clientes c2 
            WHERE c1.email = c2.email 
            AND c1.id < c2.id
        """)
        email_removidos = cursor.rowcount
        
        # Remover duplicatas de telefone (manter o mais recente)
        cursor.execute("""
            DELETE c1 FROM clientes c1
            INNER JOIN clientes c2 
            WHERE c1.telefone = c2.telefone 
            AND c1.telefone IS NOT NULL 
            AND c1.telefone != ''
            AND c1.id < c2.id
        """)
        telefone_removidos = cursor.rowcount
        
        conexao.commit()
        cursor.close()
        conexao.close()
        
        print(f"✅ {email_removidos} registros duplicados por email removidos")
        print(f"✅ {telefone_removidos} registros duplicados por telefone removidos")
        
    except Exception as e:
        print(f"❌ Erro ao limpar duplicatas: {e}")

if __name__ == "__main__":
    print("🔧 Configurando banco de dados completo")
    print("=" * 50)
    
    print("\n1. Criando tabelas necessárias...")
    criar_tabela_corretores()
    criar_tabela_imoveis()
    criar_tabela_interesses()
    
    print("\n2. Limpando duplicatas existentes...")
    limpar_duplicatas()
    
    print("\n3. Adicionando restrições únicas...")
    adicionar_indices_unicos()
    
    print("\n✅ Configuração do banco concluída!")