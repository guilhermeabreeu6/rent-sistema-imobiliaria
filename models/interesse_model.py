from db.conexao import obter_conexao
from datetime import datetime

class Interesse:
    def __init__(self, cliente_id, imovel_id, status_interesse='Ativo', data_interesse=None, observacoes=None):
        self.cliente_id = cliente_id
        self.imovel_id = imovel_id
        self.status_interesse = status_interesse
        self.data_interesse = data_interesse or datetime.now()
        self.observacoes = observacoes

    # Criar novo Interesse
    def salvar(self):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        sql = """
            INSERT INTO interesses (cliente_id, imovel_id, status_interesse, data_interesse, observacoes)
            VALUES (%s, %s, %s, %s, %s)
            """
        cursor.execute(sql, (self.cliente_id, self.imovel_id, self.status_interesse, self.data_interesse, self.observacoes))
        conexao.commit()
        conexao.close()

    # Listar todos os interesses
    @staticmethod
    def listar_todos():
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT 
                i.id, 
                i.cliente_id,
                i.imovel_id,
                c.nome AS cliente_nome,
                c.telefone AS cliente_telefone,
                im.tipo AS imovel_tipo,
                im.endereco AS imovel_endereco,
                im.valor AS imovel_valor,
                i.status_interesse AS status,
                i.data_interesse,
                i.observacoes
            FROM interesses i
            JOIN clientes c ON i.cliente_id = c.id
            JOIN imoveis im ON i.imovel_id = im.id
            ORDER BY i.data_interesse DESC
            """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        conexao.close()
        return resultados

    # Atualizar Status de interesse
    @staticmethod
    def atualizar_status(interesse_id, novo_status):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        sql = "UPDATE interesses SET status_interesse = %s WHERE id = %s"
        cursor.execute(sql, (novo_status, interesse_id))
        conexao.commit()
        conexao.close()

    # Remover um interesse
    @staticmethod
    def deletar(interesse_id):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        sql = "DELETE FROM interesses WHERE id = %s"
        cursor.execute(sql, (interesse_id,))
        conexao.commit()
        conexao.close()

    # Buscar interesse por ID
    @staticmethod
    def buscar_por_id(interesse_id):
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT 
                i.id, 
                i.cliente_id,
                i.imovel_id,
                c.nome AS cliente_nome,
                c.telefone AS cliente_telefone,
                im.tipo AS imovel_tipo,
                im.endereco AS imovel_endereco,
                im.valor AS imovel_valor,
                i.status_interesse AS status,
                i.data_interesse,
                i.observacoes
            FROM interesses i
            JOIN clientes c ON i.cliente_id = c.id
            JOIN imoveis im ON i.imovel_id = im.id
            WHERE i.id = %s
            """
        cursor.execute(sql, (interesse_id,))
        resultado = cursor.fetchone()
        conexao.close()
        return resultado