#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Script de Teste da API REST - Sistema Invistta
📊 Testa todos os endpoints da API usando test_client interno do Flask
"""

from app import app
import json

def imprimir_cabecalho():
    print("🔧 Script de Teste da API REST - Sistema Invistta")
    print("💡 Usando test_client interno do Flask")
    print()

def testar_health():
    print("🏥 Testando Health Check...")
    try:
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print(f"✅ Health Check: {response.get_json()}")
                return True
            else:
                print(f"❌ Health Check falhou: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_docs():
    print("📚 Testando GET /api/docs...")
    try:
        with app.test_client() as client:
            response = client.get('/api/docs')
            if response.status_code == 200:
                print("✅ Documentação da API carregada com sucesso")
                return True
            else:
                print(f"❌ Docs falharam: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_listar_clientes():
    print("📋 Testando GET /clientes (JSON)...")
    try:
        with app.test_client() as client:
            response = client.get('/clientes', headers={'Accept': 'application/json'})
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Listagem: {data['total']} cliente(s) encontrado(s)")
                return True
            else:
                print(f"❌ Listagem falhou: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_criar_cliente():
    print("➕ Testando POST /clientes...")
    try:
        with app.test_client() as client:
            cliente_teste = {
                'nome': 'Cliente Teste API',
                'email': 'teste.api@invistta.com',
                'telefone': '63 99999-9999'
            }
            
            response = client.post('/clientes', 
                                 headers={'Content-Type': 'application/json'},
                                 json=cliente_teste)
            
            if response.status_code == 201:
                data = response.get_json()
                print(f"✅ Cliente criado: {data['data']['nome']}")
                return True
            elif response.status_code == 409:
                print("⚠️ Cliente já existe (email duplicado)")
                return True  # Não é um erro, é validação funcionando
            else:
                print(f"❌ Criação falhou: {response.status_code}")
                print(f"Response: {response.get_json()}")
                return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_cliente_especifico():
    print("🔍 Testando GET /clientes/<id>...")
    try:
        with app.test_client() as client:
            # Primeiro, pegar a lista para obter um ID válido
            response = client.get('/clientes', headers={'Accept': 'application/json'})
            data = response.get_json()
            
            if data['total'] > 0:
                cliente_id = data['data'][0]['id']
                response = client.get(f'/clientes/{cliente_id}', headers={'Accept': 'application/json'})
                
                if response.status_code == 200:
                    cliente = response.get_json()
                    print(f"✅ Cliente encontrado: {cliente['data']['nome']}")
                    return True
                else:
                    print(f"❌ Busca falhou: {response.status_code}")
                    return False
            else:
                print("⚠️ Nenhum cliente disponível para teste")
                return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    imprimir_cabecalho()
    
    print("🚀 INICIANDO TESTES DA API REST")
    print("=" * 50)
    
    resultados = {
        'health': testar_health(),
        'docs': testar_docs(), 
        'listar': testar_listar_clientes(),
        'criar': testar_criar_cliente(),
        'buscar': testar_cliente_especifico()
    }
    
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DOS TESTES")
    print("=" * 50)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste.title()}: {status}")
    
    total_passaram = sum(resultados.values())
    total_testes = len(resultados)
    
    print(f"\n🎯 Resumo: {total_passaram}/{total_testes} testes passaram")
    
    if total_passaram == total_testes:
        print("🎉 Todos os testes passaram! API REST funcionando perfeitamente!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()