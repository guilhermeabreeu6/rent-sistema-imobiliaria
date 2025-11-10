#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏠 Modelo de Imóveis - Sistema Invistta
📊 Classe responsável pelo CRUD completo de imóveis
"""

from db.conexao import obter_conexao
import logging

class Imovel:
    def __init__(self, tipo, endereco, valor, status='disponível', corretor_id=None):
        self.tipo = tipo
        self.endereco = endereco
        self.valor = float(valor)
        self.status = status
        self.corretor_id = corretor_id
    
    def salvar(self):
        """Salva um novo imóvel no banco de dados"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            sql = """
                INSERT INTO imoveis (tipo, endereco, valor, status, corretor_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (self.tipo, self.endereco, self.valor, self.status, self.corretor_id)
            
            cursor.execute(sql, valores)
            conexao.commit()
            
            # Obter o ID do imóvel inserido
            self.id = cursor.lastrowid
            
            cursor.close()
            conexao.close()
            return True
            
        except Exception as e:
            logging.error(f"Erro ao salvar imóvel: {e}")
            return False
    
    def atualizar(self, id):
        """Atualiza um imóvel existente"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            sql = """
                UPDATE imoveis 
                SET tipo=%s, endereco=%s, valor=%s, status=%s, corretor_id=%s
                WHERE id=%s
            """
            valores = (self.tipo, self.endereco, self.valor, self.status, self.corretor_id, id)
            
            cursor.execute(sql, valores)
            conexao.commit()
            
            linhas_afetadas = cursor.rowcount
            cursor.close()
            conexao.close()
            
            return linhas_afetadas > 0
            
        except Exception as e:
            logging.error(f"Erro ao atualizar imóvel: {e}")
            return False
    
    @staticmethod
    def listar_todos():
        """Lista todos os imóveis com informações do corretor"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, 
                       c.nome as corretor_nome,
                       c.creci as corretor_creci
                FROM imoveis i
                LEFT JOIN corretores c ON i.corretor_id = c.id
                ORDER BY i.data_cadastro DESC
            """
            
            cursor.execute(sql)
            imoveis = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return imoveis
            
        except Exception as e:
            logging.error(f"Erro ao listar imóveis: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(id):
        """Busca um imóvel específico por ID"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, 
                       c.nome as corretor_nome,
                       c.creci as corretor_creci
                FROM imoveis i
                LEFT JOIN corretores c ON i.corretor_id = c.id
                WHERE i.id = %s
            """
            
            cursor.execute(sql, (id,))
            imovel = cursor.fetchone()
            
            cursor.close()
            conexao.close()
            
            return imovel
            
        except Exception as e:
            logging.error(f"Erro ao buscar imóvel por ID: {e}")
            return None
    
    @staticmethod
    def excluir(id):
        """Exclui um imóvel"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            cursor.execute("DELETE FROM imoveis WHERE id = %s", (id,))
            conexao.commit()
            
            linhas_afetadas = cursor.rowcount
            cursor.close()
            conexao.close()
            
            return linhas_afetadas > 0
            
        except Exception as e:
            logging.error(f"Erro ao excluir imóvel: {e}")
            return False
    
    @staticmethod
    def buscar_por_status(status):
        """Busca imóveis por status"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, 
                       c.nome as corretor_nome,
                       c.creci as corretor_creci
                FROM imoveis i
                LEFT JOIN corretores c ON i.corretor_id = c.id
                WHERE i.status = %s
                ORDER BY i.data_cadastro DESC
            """
            
            cursor.execute(sql, (status,))
            imoveis = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return imoveis
            
        except Exception as e:
            logging.error(f"Erro ao buscar imóveis por status: {e}")
            return []
    
    @staticmethod
    def buscar_por_tipo(tipo):
        """Busca imóveis por tipo"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, 
                       c.nome as corretor_nome,
                       c.creci as corretor_creci
                FROM imoveis i
                LEFT JOIN corretores c ON i.corretor_id = c.id
                WHERE i.tipo LIKE %s
                ORDER BY i.data_cadastro DESC
            """
            
            cursor.execute(sql, (f'%{tipo}%',))
            imoveis = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return imoveis
            
        except Exception as e:
            logging.error(f"Erro ao buscar imóveis por tipo: {e}")
            return []
    
    @staticmethod
    def contar_por_status():
        """Conta imóveis por status para estatísticas"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT status, COUNT(*) as total 
                FROM imoveis 
                GROUP BY status
            """)
            
            resultados = cursor.fetchall()
            estatisticas = {}
            
            for status, total in resultados:
                estatisticas[status] = total
            
            cursor.close()
            conexao.close()
            
            return estatisticas
            
        except Exception as e:
            logging.error(f"Erro ao contar imóveis por status: {e}")
            return {}

    @staticmethod
    def listar_corretores():
        """Lista todos os corretores disponíveis para associação"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            cursor.execute("SELECT id, nome, creci FROM corretores ORDER BY nome")
            corretores = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return corretores
            
        except Exception as e:
            logging.error(f"Erro ao listar corretores: {e}")
            return []