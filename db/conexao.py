# Conector do mysql

import mysql.connector

# Informações do banco: 

def obter_conexao():
    try: 
        conexao = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "1234",
            database = "invistta"
        )
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao Mysql: {erro}")
        return None