#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏠 Teste do CRUD de Imóveis - Sistema Invistta
📊 Testa todas as funcionalidades de imóveis
"""

from app import app
import json

def testar_crud_imoveis():
    print("🏠 TESTE COMPLETO DO CRUD DE IMÓVEIS")
    print("=" * 50)
    
    resultados = {}
    
    with app.test_client() as client:
        
        # 1. Testar listagem inicial (deve estar vazia)
        print("\n1️⃣ Testando listagem inicial...")
        response = client.get('/imoveis', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Listagem funcionando: {data['total']} imóveis encontrados")
            resultados['listar_inicial'] = True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            resultados['listar_inicial'] = False
        
        # 2. Testar cadastro de imóvel
        print("\n2️⃣ Testando cadastro de imóvel...")
        imovel_teste = {
            'tipo': 'Casa',
            'endereco': 'Rua das Palmeiras, 123, Centro, Palmas-TO',
            'valor': '350000.00',
            'status': 'disponível',
            'corretor_id': 1
        }
        
        response = client.post('/imoveis/adicionar', 
                             headers={'Content-Type': 'application/json'},
                             json=imovel_teste)
        
        if response.status_code == 201:
            data = response.get_json()
            print(f"✅ Imóvel cadastrado: {data['data']['tipo']} - {data['data']['endereco']}")
            imovel_id = data['data']['id']
            resultados['cadastro'] = True
        else:
            print(f"❌ Erro no cadastro: {response.status_code}")
            print(f"Response: {response.get_json()}")
            resultados['cadastro'] = False
            imovel_id = None
        
        # 3. Testar busca específica
        if imovel_id:
            print(f"\n3️⃣ Testando busca do imóvel #{imovel_id}...")
            response = client.get(f'/imoveis/{imovel_id}', headers={'Accept': 'application/json'})
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Imóvel encontrado: {data['data']['tipo']} - R$ {data['data']['valor']}")
                resultados['buscar'] = True
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                resultados['buscar'] = False
        else:
            resultados['buscar'] = False
        
        # 4. Testar atualização
        if imovel_id:
            print(f"\n4️⃣ Testando atualização do imóvel #{imovel_id}...")
            imovel_atualizado = {
                'tipo': 'Casa',
                'endereco': 'Rua das Palmeiras, 123, Centro, Palmas-TO (ATUALIZADO)',
                'valor': '380000.00',
                'status': 'vendido',
                'corretor_id': 1
            }
            
            response = client.put(f'/imoveis/{imovel_id}', 
                                headers={'Content-Type': 'application/json'},
                                json=imovel_atualizado)
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Imóvel atualizado: {data['message']}")
                resultados['atualizar'] = True
            else:
                print(f"❌ Erro na atualização: {response.status_code}")
                resultados['atualizar'] = False
        else:
            resultados['atualizar'] = False
        
        # 5. Testar listagem final
        print("\n5️⃣ Testando listagem final...")
        response = client.get('/imoveis', headers={'Accept': 'application/json'})
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Listagem final: {data['total']} imóveis no sistema")
            for imovel in data['data']:
                print(f"   - #{imovel['id']}: {imovel['tipo']} - {imovel['status']} - R$ {imovel['valor']}")
            resultados['listar_final'] = True
        else:
            print(f"❌ Erro na listagem final: {response.status_code}")
            resultados['listar_final'] = False
        
        # 6. Testar páginas web (templates)
        print("\n6️⃣ Testando templates HTML...")
        
        # Página de listagem
        response = client.get('/imoveis')
        if response.status_code == 200:
            print("✅ Template de listagem funcionando")
            resultados['template_listar'] = True
        else:
            print("❌ Erro no template de listagem")
            resultados['template_listar'] = False
        
        # Página de cadastro
        response = client.get('/imoveis/adicionar')
        if response.status_code == 200:
            print("✅ Template de cadastro funcionando")
            resultados['template_cadastro'] = True
        else:
            print("❌ Erro no template de cadastro")
            resultados['template_cadastro'] = False
        
        # Página de visualização
        if imovel_id:
            response = client.get(f'/imoveis/{imovel_id}')
            if response.status_code == 200:
                print("✅ Template de visualização funcionando")
                resultados['template_visualizar'] = True
            else:
                print("❌ Erro no template de visualização")
                resultados['template_visualizar'] = False
        else:
            resultados['template_visualizar'] = False
        
        # Página de edição
        if imovel_id:
            response = client.get(f'/imoveis/{imovel_id}/editar')
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
        print("🏠 CRUD de Imóveis está 100% funcional!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    return testes_passou == total_testes

if __name__ == "__main__":
    testar_crud_imoveis()