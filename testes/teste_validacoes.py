from app import app

# Teste das rotas disponíveis
with app.app_context():
    print("🔧 Verificando rotas disponíveis...")
    for rule in app.url_map.iter_rules():
        if 'delete' in rule.rule.lower() or 'delete' in rule.endpoint:
            print(f"Rota: {rule.rule} -> Endpoint: {rule.endpoint}")
    
    print("\n🔧 Testando template de clientes...")
    try:
        with app.test_client() as client:
            response = client.get('/clientes')
            if response.status_code == 200:
                print("✅ Página de clientes carregou sem erro")
            else:
                print(f"❌ Erro ao carregar página: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")