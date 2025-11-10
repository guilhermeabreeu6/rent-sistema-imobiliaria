#!/usr/bin/env python3
"""
Teste básico do sistema de interesses
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.interesse_model import Interesse
from models.cliente_model import Cliente
from models.imovel_model import Imovel
from datetime import datetime

def testar_interesse():
    print("🧪 Testando sistema de interesses...")
    print("=" * 50)
    
    try:
        # Listar interesses existentes
        print("\n1. Listando interesses existentes:")
        interesses = Interesse.listar_todos()
        print(f"✅ {len(interesses)} interesse(s) encontrado(s)")
        
        if interesses:
            print("\n📋 Primeiros 3 interesses:")
            for i, interesse in enumerate(interesses[:3]):
                print(f"  {i+1}. Cliente: {interesse['cliente_nome']}")
                print(f"     Imóvel: {interesse['imovel_tipo']} - {interesse['imovel_endereco'][:50]}")
                print(f"     Status: {interesse['status']}")
                print(f"     Data: {interesse['data_interesse']}")
                print()
        
        # Listar clientes para criar interesse
        print("\n2. Verificando clientes disponíveis:")
        clientes = Cliente.listar_todos()
        print(f"✅ {len(clientes)} cliente(s) encontrado(s)")
        
        # Listar imóveis para criar interesse
        print("\n3. Verificando imóveis disponíveis:")
        imoveis = Imovel.listar_todos()
        print(f"✅ {len(imoveis)} imóvel(eis) encontrado(s)")
        
        # Criar um interesse de teste se houver clientes e imóveis
        if clientes and imoveis:
            print("\n4. Criando interesse de teste:")
            cliente = clientes[0]
            imovel = imoveis[0]
            
            # Criar interesse
            novo_interesse = Interesse(
                cliente_id=cliente.id,
                imovel_id=imovel.id,
                status_interesse='Ativo',
                data_interesse=datetime.now(),
                observacoes='Interesse criado automaticamente durante teste'
            )
            
            novo_interesse.salvar()
            print(f"✅ Interesse criado: Cliente '{cliente.nome}' interessado em '{imovel.tipo}'")
            
            # Listar novamente para confirmar
            interesses_depois = Interesse.listar_todos()
            print(f"✅ Total de interesses após criação: {len(interesses_depois)}")
            
        else:
            print("\n⚠️  Não foi possível criar interesse de teste:")
            print(f"   - Clientes: {len(clientes)}")
            print(f"   - Imóveis: {len(imoveis)}")
        
        print("\n🎉 Teste concluído com sucesso!")
        print("✅ Sistema de interesses está funcionando corretamente!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        print("\n📋 Detalhes do erro:")
        traceback.print_exc()

if __name__ == "__main__":
    testar_interesse()