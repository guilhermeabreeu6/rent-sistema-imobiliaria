import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import sys

# Teste direto da função health
with app.app_context():
    try:
        with app.test_client() as client:
            print("🔧 Testando rota /health...")
            response = client.get('/health')
            print(f"Status: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
            print("\n🔧 Testando rota /api/docs...")
            response = client.get('/api/docs')
            print(f"Status: {response.status_code}")
            print(f"Response Type: {type(response.get_json())}")
            
            print("\n🔧 Testando rota /clientes com headers JSON...")
            response = client.get('/clientes', headers={'Accept': 'application/json'})
            print(f"Status: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()