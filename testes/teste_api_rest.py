#!/usr/bin/env python3
# 🧪 Script para testar a API REST do Sistema Invistta

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def teste_health():
    """Testa o endpoint de health check"""
    print("🏥 Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def teste_listar_clientes():
    """Testa GET /clientes"""
    print("\n📋 Testando GET /clientes (JSON)...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/clientes", headers=headers)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Sucesso: {data.get('success')}")
        print(f"Total: {data.get('total')}")
        print(f"Clientes: {len(data.get('data', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def teste_criar_cliente():
    """Testa POST /clientes"""
    print("\n➕ Testando POST /clientes...")
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            "nome": "API Test Cliente",
            "email": "api_test@example.com",
            "telefone": "(11) 98888-8888"
        }
        response = requests.post(f"{BASE_URL}/clientes", 
                               headers=headers, 
                               json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Sucesso: {result.get('success')}")
        print(f"Mensagem: {result.get('message')}")
        
        if response.status_code == 201:
            return result.get('data')
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def teste_buscar_cliente(cliente_id):
    """Testa GET /clientes/<id>"""
    print(f"\n👁️ Testando GET /clientes/{cliente_id}...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", 
                              headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Cliente: {data.get('data', {}).get('nome')}")
            return data.get('data')
        else:
            print(f"Erro: {response.json()}")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def teste_atualizar_cliente(cliente_id):
    """Testa PUT /clientes/<id>"""
    print(f"\n✏️ Testando PUT /clientes/{cliente_id}...")
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            "nome": "API Test Cliente ATUALIZADO",
            "email": "api_test_updated@example.com", 
            "telefone": "(11) 97777-7777"
        }
        response = requests.put(f"{BASE_URL}/clientes/{cliente_id}",
                              headers=headers,
                              json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Sucesso: {result.get('success')}")
        print(f"Mensagem: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def teste_excluir_cliente(cliente_id):
    """Testa DELETE /clientes/<id>"""
    print(f"\n🗑️ Testando DELETE /clientes/{cliente_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Sucesso: {result.get('success')}")
        print(f"Mensagem: {result.get('message')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def teste_documentacao():
    """Testa endpoint de documentação"""
    print(f"\n📚 Testando GET /api/docs...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/api/docs", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            docs = response.json()
            print(f"Título: {docs.get('title')}")
            print(f"Versão: {docs.get('version')}")
            print(f"Endpoints: {len(docs.get('endpoints', {}))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def executar_testes_completos():
    """Executa todos os testes da API REST"""
    print("🚀 INICIANDO TESTES DA API REST")
    print("=" * 50)
    
    resultados = []
    
    # 1. Health Check
    resultados.append(("Health Check", teste_health()))
    
    # 2. Documentação
    resultados.append(("Documentação", teste_documentacao()))
    
    # 3. Listar clientes
    resultados.append(("Listar Clientes", teste_listar_clientes()))
    
    # 4. Criar cliente
    cliente_criado = teste_criar_cliente()
    resultados.append(("Criar Cliente", cliente_criado is not None))
    
    if cliente_criado:
        # Assumir que o último cliente criado terá um ID
        # Para uma implementação real, você retornaria o ID do cliente criado
        print("\n🔍 Buscando último cliente para obter ID...")
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/clientes", headers=headers)
        if response.status_code == 200:
            clientes = response.json().get('data', [])
            if clientes:
                ultimo_cliente = clientes[-1]  # Último cliente
                cliente_id = ultimo_cliente.get('id')
                
                # 5. Buscar cliente específico
                cliente_encontrado = teste_buscar_cliente(cliente_id)
                resultados.append(("Buscar Cliente", cliente_encontrado is not None))
                
                # 6. Atualizar cliente
                resultados.append(("Atualizar Cliente", teste_atualizar_cliente(cliente_id)))
                
                # 7. Excluir cliente
                resultados.append(("Excluir Cliente", teste_excluir_cliente(cliente_id)))
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DOS TESTES")
    print("=" * 50)
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{nome}: {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\n🎯 Resumo: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM! API REST está funcionando perfeitamente!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    print("🔧 Script de Teste da API REST - Sistema Invistta")
    print("💡 Certifique-se que o servidor Flask está rodando na porta 5000")
    input("⏸️ Pressione ENTER para continuar...")
    
    executar_testes_completos()