# 🌐 API REST - Exemplos de Uso

## 📋 Endpoints Disponíveis

### 1. Health Check
```bash
curl -X GET http://localhost:5000/health
```

### 2. Listar Todos os Clientes

**Como JSON (API):**
```bash
curl -X GET http://localhost:5000/clientes \
  -H "Accept: application/json"
```

**Como HTML (Web):**
```bash
curl -X GET http://localhost:5000/clientes
```

### 3. Buscar Cliente Específico

**Como JSON:**
```bash
curl -X GET http://localhost:5000/clientes/1 \
  -H "Accept: application/json"
```

### 4. Criar Novo Cliente

```bash
curl -X POST http://localhost:5000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@email.com",
    "telefone": "(11) 99999-9999"
  }'
```

### 5. Atualizar Cliente

```bash
curl -X PUT http://localhost:5000/clientes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva Santos",
    "email": "joao.santos@email.com",
    "telefone": "(11) 98888-8888"
  }'
```

### 6. Excluir Cliente

```bash
curl -X DELETE http://localhost:5000/clientes/1
```

### 7. Documentação da API

```bash
curl -X GET http://localhost:5000/api/docs \
  -H "Accept: application/json"
```

## 📊 Códigos de Status HTTP

| Código | Significado | Quando Ocorre |
|--------|-------------|---------------|
| 200    | OK          | Operação bem-sucedida |
| 201    | Created     | Cliente criado com sucesso |
| 400    | Bad Request | Dados inválidos ou ausentes |
| 404    | Not Found   | Cliente não encontrado |
| 409    | Conflict    | Email/telefone já existe |
| 500    | Server Error| Erro interno do servidor |

## 🔧 Testando com Python

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Listar clientes
response = requests.get(f"{BASE_URL}/clientes", 
                       headers={'Accept': 'application/json'})
print(response.json())

# Criar cliente
data = {
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "telefone": "(11) 97777-7777"
}
response = requests.post(f"{BASE_URL}/clientes",
                        headers={'Content-Type': 'application/json'},
                        json=data)
print(response.json())

# Atualizar cliente
data_update = {
    "nome": "Maria Santos Silva",
    "email": "maria.silva@email.com",
    "telefone": "(11) 96666-6666"
}
response = requests.put(f"{BASE_URL}/clientes/1",
                       headers={'Content-Type': 'application/json'},
                       json=data_update)
print(response.json())

# Excluir cliente
response = requests.delete(f"{BASE_URL}/clientes/1")
print(response.json())
```

## 🎯 Integração com Frontend

### React.js Exemplo

```javascript
// Cliente service
class ClienteService {
  static baseURL = 'http://localhost:5000';

  // Listar todos
  static async listar() {
    const response = await fetch(`${this.baseURL}/clientes`, {
      headers: { 'Accept': 'application/json' }
    });
    return response.json();
  }

  // Buscar por ID
  static async buscarPorId(id) {
    const response = await fetch(`${this.baseURL}/clientes/${id}`, {
      headers: { 'Accept': 'application/json' }
    });
    return response.json();
  }

  // Criar cliente
  static async criar(cliente) {
    const response = await fetch(`${this.baseURL}/clientes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(cliente)
    });
    return response.json();
  }

  // Atualizar cliente
  static async atualizar(id, cliente) {
    const response = await fetch(`${this.baseURL}/clientes/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(cliente)
    });
    return response.json();
  }

  // Excluir cliente
  static async excluir(id) {
    const response = await fetch(`${this.baseURL}/clientes/${id}`, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' }
    });
    return response.json();
  }
}

// Uso em componente React
const ListaClientes = () => {
  const [clientes, setClientes] = useState([]);

  useEffect(() => {
    ClienteService.listar()
      .then(data => {
        if (data.success) {
          setClientes(data.data);
        }
      });
  }, []);

  const excluirCliente = async (id) => {
    if (confirm('Tem certeza?')) {
      const result = await ClienteService.excluir(id);
      if (result.success) {
        setClientes(clientes.filter(c => c.id !== id));
        alert(result.message);
      }
    }
  };

  return (
    <div>
      {clientes.map(cliente => (
        <div key={cliente.id}>
          <h3>{cliente.nome}</h3>
          <p>{cliente.email}</p>
          <button onClick={() => excluirCliente(cliente.id)}>
            Excluir
          </button>
        </div>
      ))}
    </div>
  );
};
```

## 🔒 CORS para Frontend

Para permitir acesso do frontend, adicione ao Flask:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite todas as origens

# Ou configuração específica:
CORS(app, origins=['http://localhost:3000'])  # Apenas React dev
```

## 📱 App Mobile (React Native)

```javascript
// services/ClienteAPI.js
const API_BASE = 'http://192.168.1.100:5000'; // IP da sua máquina

export const ClienteAPI = {
  async listar() {
    const response = await fetch(`${API_BASE}/clientes`, {
      headers: { 'Accept': 'application/json' }
    });
    return await response.json();
  },

  async criar(cliente) {
    const response = await fetch(`${API_BASE}/clientes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(cliente)
    });
    return await response.json();
  }
};
```

## 🧪 Testes Automatizados

Execute o script de teste:
```bash
python teste_api_rest.py
```

Ou instale as dependências e rode:
```bash
pip install requests
python teste_api_rest.py
```

## 📈 Monitoramento

### Logs de Acesso
O Flask automaticamente loga todas as requisições no console.

### Métricas Básicas
```bash
# Ver quantos clientes
curl -s http://localhost:5000/clientes?format=json | jq '.total'

# Status da aplicação  
curl -s http://localhost:5000/health | jq '.status'
```

---

**🎉 API REST Completa e Funcional!**

Agora você tem uma API que pode ser consumida por:
- ✅ Frontend React/Vue/Angular
- ✅ Apps Mobile
- ✅ Outros serviços
- ✅ Scripts Python
- ✅ Comandos curl