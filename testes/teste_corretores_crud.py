#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
👨‍💼 Teste do CRUD de Corretores - Sistema Invistta
📊 Testa todas as funcionalidades de corretores
"""

from app import app
import json

def testar_crud_corretores():
    print("👨‍💼 TESTE COMPLETO DO CRUD DE CORRETORES")
    print("=" * 50)
    
    resultados = {}
    
    with app.test_client() as client:
        
        # 1. Testar listagem inicial
        print("\n1️⃣ Testando listagem inicial...")
        response = client.get('/corretores', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Listagem funcionando: {data['total']} corretores encontrados")
            print(f"   Estatísticas: {data['estatisticas']}")
            resultados['listar_inicial'] = True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            resultados['listar_inicial'] = False
        
        # 2. Testar cadastro de corretor
        print("\n2️⃣ Testando cadastro de corretor...")
        corretor_teste = {
            'nome': 'Ana Silva Santos',
            'email': 'ana@invistta.com',
            'telefone': '(63) 99888-7777',
            'creci': 'CRECI-54321'
        }
        
        response = client.post('/corretores/adicionar', 
                             headers={'Content-Type': 'application/json'},
                             json=corretor_teste)
        
        if response.status_code == 201:
            data = response.get_json()
            print(f"✅ Corretor cadastrado: {data['data']['nome']} - {data['data']['email']}")
            corretor_id = data['data']['id']
            resultados['cadastro'] = True
        else:
            print(f"❌ Erro no cadastro: {response.status_code}")
            print(f"Response: {response.get_json()}")
            resultados['cadastro'] = False
            corretor_id = None
        
        # 3. Testar busca específica
        if corretor_id:
            print(f"\n3️⃣ Testando busca do corretor #{corretor_id}...")
            response = client.get(f'/corretores/{corretor_id}', headers={'Accept': 'application/json'})
            
            if response.status_code == 200:
                data = response.get_json()
                corretor = data['data']['corretor']
                print(f"✅ Corretor encontrado: {corretor['nome']} - CRECI: {corretor.get('creci', 'N/A')}")
                resultados['buscar'] = True
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                resultados['buscar'] = False
        else:
            resultados['buscar'] = False
        
        # 4. Testar atualização
        if corretor_id:
            print(f"\n4️⃣ Testando atualização do corretor #{corretor_id}...")
            corretor_atualizado = {
                'nome': 'Ana Silva Santos (Atualizada)',
                'email': 'ana.santos@invistta.com',
                'telefone': '(63) 99888-7777',
                'creci': 'CRECI/TO 54321'
            }
            
            response = client.put(f'/corretores/{corretor_id}', 
                                headers={'Content-Type': 'application/json'},
                                json=corretor_atualizado)
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Corretor atualizado: {data['message']}")
                resultados['atualizar'] = True
            else:
                print(f"❌ Erro na atualização: {response.status_code}")
                print(f"Response: {response.get_json()}")
                resultados['atualizar'] = False
        else:
            resultados['atualizar'] = False
        
        # 5. Testar validação de email duplicado
        print("\n5️⃣ Testando validação de email duplicado...")
        corretor_duplicado = {
            'nome': 'João Duplicado',
            'email': 'ana.santos@invistta.com',  # Email já existe
            'telefone': '(63) 99999-9999',
            'creci': 'CRECI-99999'
        }
        
        response = client.post('/corretores/adicionar', 
                             headers={'Content-Type': 'application/json'},
                             json=corretor_duplicado)
        
        if response.status_code == 409:  # Conflict
            print("✅ Validação de email duplicado funcionando")
            resultados['validacao_email'] = True
        else:
            print(f"❌ Validação falhou: {response.status_code}")
            resultados['validacao_email'] = False
        
        # 6. Testar listagem final
        print("\n6️⃣ Testando listagem final...")
        response = client.get('/corretores', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Listagem final: {data['total']} corretores no sistema")
            for corretor in data['data']:
                print(f"   - #{corretor['id']}: {corretor['nome']} - {corretor['email']}")
            resultados['listar_final'] = True
        else:
            print(f"❌ Erro na listagem final: {response.status_code}")
            resultados['listar_final'] = False
        
        # 7. Testar templates HTML
        print("\n7️⃣ Testando templates HTML...")
        
        # Página de listagem
        response = client.get('/corretores')
        if response.status_code == 200:
            print("✅ Template de listagem funcionando")
            resultados['template_listar'] = True
        else:
            print("❌ Erro no template de listagem")
            resultados['template_listar'] = False
        
        # Página de cadastro
        response = client.get('/corretores/adicionar')
        if response.status_code == 200:
            print("✅ Template de cadastro funcionando")
            resultados['template_cadastro'] = True
        else:
            print("❌ Erro no template de cadastro")
            resultados['template_cadastro'] = False
        
        # Página de visualização
        if corretor_id:
            response = client.get(f'/corretores/{corretor_id}')
            if response.status_code == 200:
                print("✅ Template de visualização funcionando")
                resultados['template_visualizar'] = True
            else:
                print("❌ Erro no template de visualização")
                resultados['template_visualizar'] = False
        else:
            resultados['template_visualizar'] = False
        
        # Página de edição
        if corretor_id:
            response = client.get(f'/corretores/{corretor_id}/editar')
            if response.status_code == 200:
                print("✅ Template de edição funcionando")
                resultados['template_editar'] = True
            else:
                print("❌ Erro no template de edição")
                resultados['template_editar'] = False
        else:
            resultados['template_editar'] = False
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    total_testes = len(resultados)
    testes_passou = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Resumo: {testes_passou}/{total_testes} testes passaram")
    
    if testes_passou == total_testes:
        print("🎉 PARABÉNS! Todos os testes passaram!")
        print("👨‍💼 CRUD de Corretores está 100% funcional!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    return testes_passou == total_testes

if __name__ == "__main__":
    testar_crud_corretores()