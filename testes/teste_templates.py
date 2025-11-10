#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Teste específico para templates de cliente"""

from app import app
import random

def testar_templates_cliente():
    email_unico = f'test.template.{random.randint(1000,9999)}@test.com'
    
    with app.test_client() as client:
        # Primeiro criar um cliente para testar
        response = client.post('/clientes', 
                              headers={'Content-Type': 'application/json'},
                              json={'nome': 'Test Visualizar', 'email': email_unico, 'telefone': f'{random.randint(100000,999999)}'})
        print(f'Criação: {response.status_code}')
        
        if response.status_code == 201:
            # Buscar o cliente para obter o ID
            response = client.get('/clientes', headers={'Accept': 'application/json'})
            if response.status_code == 200:
                clientes = response.get_json()['data']
                for cliente in clientes:
                    if cliente['email'] == email_unico:
                        cliente_id = cliente['id']
                        print(f'Cliente ID encontrado: {cliente_id}')
                        
                        # Testar visualização HTML
                        response = client.get(f'/clientes/{cliente_id}')
                        print(f'Visualização HTML: {response.status_code}')
                        
                        # Testar edição HTML  
                        response = client.get(f'/clientes/editar/{cliente_id}')
                        print(f'Edição HTML: {response.status_code}')
                        
                        if response.status_code == 200:
                            print("✅ Todos os templates de cliente funcionando!")
                        else:
                            print("❌ Problemas com templates")
                        break
        else:
            print("❌ Falha ao criar cliente de teste")

if __name__ == "__main__":
    testar_templates_cliente()