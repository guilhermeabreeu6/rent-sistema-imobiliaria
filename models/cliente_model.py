from db.conexao import obter_conexao
import mysql.connector

class Cliente:
    def __init__(self, nome, email, telefone):
        self.nome = nome
        self.email = email
        self.telefone = telefone

    @staticmethod
    def email_existe(email):
        """Verifica se o email já está cadastrado"""
        conexao = obter_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id FROM clientes WHERE email = %s", (email,))
            resultado = cursor.fetchone()
            cursor.close()
            conexao.close()
            return resultado is not None
        return False
    
    @staticmethod
    def telefone_existe(telefone):
        """Verifica se o telefone já está cadastrado"""
        if not telefone:  # Se telefone estiver vazio, não verifica
            return False
        conexao = obter_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id FROM clientes WHERE telefone = %s", (telefone,))
            resultado = cursor.fetchone()
            cursor.close()
            conexao.close()
            return resultado is not None
        return False

    def salvar(self):
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                comando = "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)"
                valores = (self.nome, self.email, self.telefone)
                cursor.execute(comando, valores)
                conexao.commit()
                cursor.close()
                conexao.close()
                return True
            except mysql.connector.IntegrityError as e:
                conexao.close()
                if "uk_cliente_email" in str(e):
                    raise ValueError("Email já cadastrado")
                elif "uk_cliente_telefone" in str(e):
                    raise ValueError("Telefone já cadastrado")
                else:
                    raise ValueError(f"Erro de integridade: {e}")
            except Exception as e:
                conexao.close()
                raise e
        return False

    @staticmethod
    def buscar_por_id(id):
        """Busca um cliente por ID"""
        conexao = obter_conexao()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
            cliente = cursor.fetchone()
            cursor.close()
            conexao.close()
            return cliente
        return None

    @staticmethod
    def listar_todos():
        """Lista todos os clientes"""
        conexao = obter_conexao()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes ORDER BY id ASC")
            clientes = cursor.fetchall()
            cursor.close()
            conexao.close()
            return clientes
        return []

    @staticmethod
    def excluir(id):
        """Exclui um cliente por ID"""
        conexao = obter_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
            linhas_afetadas = cursor.rowcount
            conexao.commit()
            cursor.close()
            conexao.close()
            return linhas_afetadas > 0
        return False

    def atualizar(self, id):
        """Atualiza os dados de um cliente"""
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                comando = """
                    UPDATE clientes 
                    SET nome = %s, email = %s, telefone = %s 
                    WHERE id = %s
                """
                valores = (self.nome, self.email, self.telefone, id)
                cursor.execute(comando, valores)
                linhas_afetadas = cursor.rowcount
                conexao.commit()
                cursor.close()
                conexao.close()
                return linhas_afetadas > 0
            except mysql.connector.IntegrityError as e:
                conexao.close()
                if "uk_cliente_email" in str(e):
                    raise ValueError("Email já cadastrado para outro cliente")
                elif "uk_cliente_telefone" in str(e):
                    raise ValueError("Telefone já cadastrado para outro cliente")
                else:
                    raise ValueError(f"Erro de integridade: {e}")
            except Exception as e:
                conexao.close()
                raise e
        return False