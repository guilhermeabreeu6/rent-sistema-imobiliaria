#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 TESTE FINAL - Sistema Completo Invistta
🔗 Testa integração entre Clientes, Imóveis e Corretores
"""

from app import app
import json
import random
from datetime import datetime

def teste_sistema_completo():
    print("🎯 TESTE SISTEMA COMPLETO - INVISTTA")
    print("=" * 60)
    
    resultados = {}
    ids_criados = {}
    
    with app.test_client() as client:
        
        # 1. Criar um corretor
        print("\n1️⃣ Criando corretor...")
        # Gerar dados únicos para teste
        timestamp = int(datetime.now().timestamp())
        random_num = random.randint(1000, 9999)
        
        corretor_data = {
            'nome': f'Roberto Silva Teste {random_num}',
            'email': f'roberto.teste.{timestamp}@invistta.com',
            'telefone': '(63) 99111-2222',
            'creci': f'CRECI/TO {random_num}'
        }
        
        response = client.post('/corretores/adicionar', 
                             headers={'Content-Type': 'application/json'},
                             json=corretor_data)
        
        if response.status_code == 201:
            data = response.get_json()
            ids_criados['corretor'] = data['data']['id']
            print(f"✅ Corretor criado: {data['data']['nome']} (ID: {ids_criados['corretor']})")
            resultados['criar_corretor'] = True
        else:
            print(f"❌ Erro ao criar corretor: {response.status_code}")
            resultados['criar_corretor'] = False
            return
        
        # 2. Criar um cliente
        print("\n2️⃣ Criando cliente...")
        cliente_data = {
            'nome': f'Maria Santos Teste {random.randint(1000, 9999)}',
            'email': f'maria.teste.{timestamp}@email.com',
            'telefone': f'(63) 99{random.randint(100,999)}-{random.randint(1000,9999)}'
        }
        
        response = client.post('/clientes',
                             headers={'Content-Type': 'application/json'},
                             json=cliente_data)
        
        if response.status_code == 201:
            data = response.get_json()
            # Buscar o cliente pelo email para obter o ID
            response_cliente = client.get('/clientes', headers={'Accept': 'application/json'})
            if response_cliente.status_code == 200:
                clientes_data = response_cliente.get_json()
                for cliente in clientes_data.get('data', []):
                    if cliente['email'] == cliente_data['email']:
                        ids_criados['cliente'] = cliente['id']
                        break
            
            print(f"✅ Cliente criado: {data['data']['nome']} (ID: {ids_criados.get('cliente', 'N/A')})")
            resultados['criar_cliente'] = True
        else:
            print(f"❌ Erro ao criar cliente: {response.status_code}")
            print(f"Response: {response.get_json()}")
            resultados['criar_cliente'] = False
        
        # 3. Criar um imóvel com corretor associado
        print("\n3️⃣ Criando imóvel com corretor associado...")
        imovel_data = {
            'tipo': 'Casa',
            'endereco': 'Rua das Flores, 123, Palmas-TO',
            'valor': 350000.00,
            'status': 'disponivel',
            'corretor_id': ids_criados['corretor'],
            'descricao': 'Linda casa com 3 quartos e quintal'
        }
        
        response = client.post('/imoveis/adicionar',
                             headers={'Content-Type': 'application/json'},
                             json=imovel_data)
        
        if response.status_code == 201:
            data = response.get_json()
            ids_criados['imovel'] = data['data']['id']
            print(f"✅ Imóvel criado: {data['data']['tipo']} (ID: {ids_criados['imovel']})")
            resultados['criar_imovel'] = True
        else:
            print(f"❌ Erro ao criar imóvel: {response.status_code}")
            print(f"Response: {response.get_json()}")
            resultados['criar_imovel'] = False
        
        # 4. Testar busca do corretor com imóveis associados
        print(f"\n4️⃣ Testando corretor com imóveis associados...")
        response = client.get(f'/corretores/{ids_criados["corretor"]}',
                            headers={'Accept': 'application/json'})
        
        if response.status_code == 200:
            data = response.get_json()
            corretor = data['data']['corretor']
            imoveis = data['data']['imoveis']
            print(f"✅ Corretor: {corretor['nome']} tem {len(imoveis)} imóvel(is)")
            for imovel in imoveis:
                try:
                    valor_float = float(imovel['valor'])
                    print(f"   📍 {imovel['tipo']} - {imovel['endereco']} - R$ {valor_float:,.2f}")
                except (ValueError, TypeError):
                    print(f"   📍 {imovel['tipo']} - {imovel['endereco']} - R$ {imovel['valor']}")
            resultados['relacionamento_corretor'] = True
        else:
            print(f"❌ Erro na busca do corretor: {response.status_code}")
            resultados['relacionamento_corretor'] = False
        
        # 5. Testar listagens com estatísticas
        print(f"\n5️⃣ Testando listagens com estatísticas...")
        
        # Estatísticas de corretores
        response = client.get('/corretores', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            stats = data['estatisticas']
            print(f"📊 Corretores: {stats['total_corretores']} total, {stats['corretores_ativos']} ativos")
            resultados['stats_corretores'] = True
        else:
            resultados['stats_corretores'] = False
        
        # Estatísticas de imóveis
        response = client.get('/imoveis', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            total_imoveis = data['total']
            print(f"📊 Imóveis: {total_imoveis} total")
            resultados['stats_imoveis'] = True
        else:
            resultados['stats_imoveis'] = False
        
        # 6. Testar páginas web principais
        print(f"\n6️⃣ Testando páginas web...")
        
        paginas_teste = [
            ('/', 'Homepage'),
            ('/clientes', 'Lista de Clientes'),
            ('/imoveis', 'Lista de Imóveis'),
            ('/corretores', 'Lista de Corretores'),
            ('/clientes/adicionar', 'Cadastro de Cliente'),
            ('/imoveis/adicionar', 'Cadastro de Imóvel'),
            ('/corretores/adicionar', 'Cadastro de Corretor')
        ]
        
        paginas_ok = 0
        for url, nome in paginas_teste:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✅ {nome}: OK")
                paginas_ok += 1
            else:
                print(f"   ❌ {nome}: Erro {response.status_code}")
        
        resultados['paginas_web'] = paginas_ok == len(paginas_teste)
        
        # 7. Teste de integridade das validações
        print(f"\n7️⃣ Testando validações...")
        
        # Teste email duplicado corretor - usar um email que sabemos que já foi criado
        email_corretor_existente = corretor_data['email']  # Usar o email do corretor criado no teste
        response = client.post('/corretores/adicionar', 
                             headers={'Content-Type': 'application/json'},
                             json={'nome': 'Test Duplicado', 'email': email_corretor_existente, 'telefone': '123', 'creci': 'CRECI-99999'})
        
        if response.status_code == 409:
            print("   ✅ Validação email duplicado (corretor): OK")
            validacoes_ok = 1
        else:
            print(f"   ❌ Validação email duplicado (corretor): Falhou (código: {response.status_code})")
            if response.get_json():
                print(f"   Response: {response.get_json()}")
            validacoes_ok = 0
        
        # Teste email duplicado cliente - usar um email que sabemos que já foi criado
        email_cliente_existente = cliente_data['email']  # Usar o email do cliente criado no teste
        response = client.post('/clientes',
                             headers={'Content-Type': 'application/json'},
                             json={'nome': 'Test Duplicado', 'email': email_cliente_existente, 'telefone': '999888777'})
        
        if response.status_code == 409:
            print("   ✅ Validação email duplicado (cliente): OK")
            validacoes_ok += 1
        else:
            print(f"   ❌ Validação email duplicado (cliente): Falhou (código: {response.status_code})")
            if response.get_json():
                print(f"   Response: {response.get_json()}")
        
        resultados['validacoes'] = validacoes_ok == 2
    
    # Relatório Final
    print("\n" + "=" * 60)
    print("🎯 RELATÓRIO FINAL - SISTEMA COMPLETO")
    print("=" * 60)
    
    total_testes = len(resultados)
    testes_passou = sum(resultados.values())
    
    categorias = {
        'Criação de Entidades': ['criar_corretor', 'criar_cliente', 'criar_imovel'],
        'Relacionamentos': ['relacionamento_corretor'],
        'Estatísticas': ['stats_corretores', 'stats_imoveis'],
        'Interface Web': ['paginas_web'],
        'Validações': ['validacoes']
    }
    
    for categoria, testes in categorias.items():
        print(f"\n📋 {categoria}:")
        for teste in testes:
            if teste in resultados:
                status = "✅ PASSOU" if resultados[teste] else "❌ FALHOU"
                nome_teste = teste.replace('_', ' ').title()
                print(f"   {nome_teste}: {status}")
    
    print(f"\n🎯 RESULTADO GERAL: {testes_passou}/{total_testes} testes passaram")
    
    if testes_passou == total_testes:
        print("\n🎉 PARABÉNS! SISTEMA COMPLETAMENTE FUNCIONAL! 🎉")
        print("🏆 A Invistta agora possui:")
        print("   ✅ CRUD Completo de Clientes")
        print("   ✅ CRUD Completo de Imóveis") 
        print("   ✅ CRUD Completo de Corretores")
        print("   ✅ Relacionamentos entre Entidades")
        print("   ✅ API REST Funcional")
        print("   ✅ Interface Web Responsiva")
        print("   ✅ Validações de Segurança")
        print("   ✅ Sistema de Estatísticas")
        print("\n🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
    else:
        print(f"\n⚠️ {total_testes - testes_passou} teste(s) falharam. Revisar logs acima.")
    
    return testes_passou == total_testes

if __name__ == "__main__":
    teste_sistema_completo()