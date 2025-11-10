#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
👨‍💼 Modelo de Corretores - Sistema Invistta
📊 Classe responsável pelo CRUD completo de corretores
"""

from db.conexao import obter_conexao
import logging
import re

class Corretor:
    def __init__(self, nome, email, telefone=None, creci=None):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.creci = creci
    
    def salvar(self):
        """Salva um novo corretor no banco de dados"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            sql = """
                INSERT INTO corretores (nome, email, telefone, creci) 
                VALUES (%s, %s, %s, %s)
            """
            valores = (self.nome, self.email, self.telefone, self.creci)
            
            cursor.execute(sql, valores)
            conexao.commit()
            
            # Obter o ID do corretor inserido
            self.id = cursor.lastrowid
            
            cursor.close()
            conexao.close()
            return True
            
        except Exception as e:
            logging.error(f"Erro ao salvar corretor: {e}")
            # Verificar se é erro de duplicata
            if "Duplicate entry" in str(e):
                if "email" in str(e):
                    raise ValueError("Este email já está cadastrado!")
                elif "creci" in str(e):
                    raise ValueError("Este CRECI já está cadastrado!")
            raise ValueError(f"Erro ao salvar corretor: {str(e)}")
    
    def atualizar(self, id):
        """Atualiza um corretor existente"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            sql = """
                UPDATE corretores 
                SET nome=%s, email=%s, telefone=%s, creci=%s
                WHERE id=%s
            """
            valores = (self.nome, self.email, self.telefone, self.creci, id)
            
            cursor.execute(sql, valores)
            conexao.commit()
            
            linhas_afetadas = cursor.rowcount
            cursor.close()
            conexao.close()
            
            return linhas_afetadas > 0
            
        except Exception as e:
            logging.error(f"Erro ao atualizar corretor: {e}")
            # Verificar se é erro de duplicata
            if "Duplicate entry" in str(e):
                if "email" in str(e):
                    raise ValueError("Este email já está cadastrado!")
                elif "creci" in str(e):
                    raise ValueError("Este CRECI já está cadastrado!")
            raise ValueError(f"Erro ao atualizar corretor: {str(e)}")
    
    @staticmethod
    def listar_todos():
        """Lista todos os corretores com contagem de imóveis"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT c.*, 
                       COUNT(i.id) as total_imoveis,
                       COUNT(CASE WHEN i.status = 'disponível' THEN 1 END) as imoveis_disponiveis,
                       COUNT(CASE WHEN i.status = 'vendido' THEN 1 END) as imoveis_vendidos,
                       COUNT(CASE WHEN i.status = 'alugado' THEN 1 END) as imoveis_alugados
                FROM corretores c
                LEFT JOIN imoveis i ON c.id = i.corretor_id
                GROUP BY c.id
                ORDER BY c.data_cadastro DESC
            """
            
            cursor.execute(sql)
            corretores = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return corretores
            
        except Exception as e:
            logging.error(f"Erro ao listar corretores: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(id):
        """Busca um corretor específico por ID com estatísticas"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT c.*, 
                       COUNT(i.id) as total_imoveis,
                       COUNT(CASE WHEN i.status = 'disponível' THEN 1 END) as imoveis_disponiveis,
                       COUNT(CASE WHEN i.status = 'vendido' THEN 1 END) as imoveis_vendidos,
                       COUNT(CASE WHEN i.status = 'alugado' THEN 1 END) as imoveis_alugados
                FROM corretores c
                LEFT JOIN imoveis i ON c.id = i.corretor_id
                WHERE c.id = %s
                GROUP BY c.id
            """
            
            cursor.execute(sql, (id,))
            corretor = cursor.fetchone()
            
            cursor.close()
            conexao.close()
            
            return corretor
            
        except Exception as e:
            logging.error(f"Erro ao buscar corretor por ID: {e}")
            return None
    
    @staticmethod
    def excluir(id):
        """Exclui um corretor (apenas se não tiver imóveis associados)"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            # Verificar se tem imóveis associados
            cursor.execute("SELECT COUNT(*) FROM imoveis WHERE corretor_id = %s", (id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.close()
                conexao.close()
                raise ValueError(f"Não é possível excluir: o corretor possui {count} imóvel(is) associado(s)!")
            
            # Excluir corretor
            cursor.execute("DELETE FROM corretores WHERE id = %s", (id,))
            conexao.commit()
            
            linhas_afetadas = cursor.rowcount
            cursor.close()
            conexao.close()
            
            return linhas_afetadas > 0
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logging.error(f"Erro ao excluir corretor: {e}")
            return False
    
    @staticmethod
    def buscar_imoveis_do_corretor(id):
        """Busca todos os imóveis de um corretor específico"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor(dictionary=True)
            
            sql = """
                SELECT * FROM imoveis 
                WHERE corretor_id = %s
                ORDER BY data_cadastro DESC
            """
            
            cursor.execute(sql, (id,))
            imoveis = cursor.fetchall()
            
            cursor.close()
            conexao.close()
            
            return imoveis
            
        except Exception as e:
            logging.error(f"Erro ao buscar imóveis do corretor: {e}")
            return []
    
    @staticmethod
    def email_existe(email, id_excluir=None):
        """Verifica se email já está cadastrado"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            if id_excluir:
                # Para update - excluir o próprio registro da verificação
                cursor.execute(
                    "SELECT COUNT(*) FROM corretores WHERE email = %s AND id != %s", 
                    (email, id_excluir)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM corretores WHERE email = %s", (email,))
            
            existe = cursor.fetchone()[0] > 0
            
            cursor.close()
            conexao.close()
            
            return existe
            
        except Exception as e:
            logging.error(f"Erro ao verificar email: {e}")
            return False
    
    @staticmethod
    def creci_existe(creci, id_excluir=None):
        """Verifica se CRECI já está cadastrado"""
        if not creci:
            return False
            
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            if id_excluir:
                # Para update - excluir o próprio registro da verificação
                cursor.execute(
                    "SELECT COUNT(*) FROM corretores WHERE creci = %s AND id != %s", 
                    (creci, id_excluir)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM corretores WHERE creci = %s", (creci,))
            
            existe = cursor.fetchone()[0] > 0
            
            cursor.close()
            conexao.close()
            
            return existe
            
        except Exception as e:
            logging.error(f"Erro ao verificar CRECI: {e}")
            return False
    
    @staticmethod
    def validar_email(email):
        """Valida formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_creci(creci):
        """Valida formato do CRECI"""
        if not creci:
            return True  # CRECI é opcional
        
        # Remover espaços e converter para uppercase
        creci_clean = creci.upper().strip()
        
        # Verificar padrão: CRECI-XXXXX ou CRECI/XX XXXXX
        patterns = [
            r'^CRECI-\d{4,6}$',  # CRECI-12345
            r'^CRECI/[A-Z]{2}\s?\d{4,6}$',  # CRECI/TO 12345 ou CRECI/TO12345
            r'^\d{4,6}$'  # Apenas números
        ]
        
        for pattern in patterns:
            if re.match(pattern, creci_clean):
                return True
        
        return False
    
    @staticmethod
    def contar_estatisticas():
        """Retorna estatísticas gerais dos corretores"""
        try:
            conexao = obter_conexao()
            cursor = conexao.cursor()
            
            stats = {}
            
            # Total de corretores
            cursor.execute("SELECT COUNT(*) FROM corretores")
            stats['total_corretores'] = cursor.fetchone()[0]
            
            # Corretores com imóveis
            cursor.execute("""
                SELECT COUNT(DISTINCT corretor_id) 
                FROM imoveis 
                WHERE corretor_id IS NOT NULL
            """)
            stats['corretores_ativos'] = cursor.fetchone()[0]
            
            # Corretores sem imóveis
            stats['corretores_inativos'] = stats['total_corretores'] - stats['corretores_ativos']
            
            cursor.close()
            conexao.close()
            
            return stats
            
        except Exception as e:
            logging.error(f"Erro ao contar estatísticas: {e}")
            return {
                'total_corretores': 0,
                'corretores_ativos': 0,
                'corretores_inativos': 0
            }