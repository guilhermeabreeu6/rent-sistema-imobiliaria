# RENT - Sistema de Inteligência Imobiliária

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Descrição

O **RENT - Sistema de Inteligência Imobiliária** é uma aplicação web completa desenvolvida em Flask para gerenciamento de negócios imobiliários. O sistema oferece funcionalidades abrangentes para administrar clientes, corretores, imóveis e interesses de compra/locação.

## ✨ Funcionalidades

### 🏠 Gestão de Imóveis
- Cadastro completo de imóveis com informações detalhadas
- Tipos suportados: Casa, Apartamento, Kitnet, Studio, Sobrado, Cobertura, Terreno, Comercial, Industrial
- Controle de status (Disponível, Vendido, Alugado, Reservado)
- Gerenciamento de finalidades (Venda, Aluguel, Venda/Aluguel)
- Upload e gerenciamento de imagens
- Campos detalhados: quartos, banheiros, vagas de garagem, área, valor

### 👥 Gestão de Clientes
- Cadastro completo de clientes interessados
- Informações de contato (telefone, email)
- Histórico de interesses e interações
- Sistema de observações e anotações

### 👨‍💼 Gestão de Corretores
- Cadastro de corretores com CRECI
- Atribuição de imóveis por corretor
- Controle de vendas e comissões
- Informações de contato e endereço

### 💝 Sistema de Interesses
- Registro de interesses de clientes por imóveis
- Status de acompanhamento (Ativo, Finalizado, Cancelado)
- Data de interesse e observações
- Relacionamento cliente-imóvel

### 📊 Dashboard e Relatórios
- Visão geral do sistema
- Estatísticas de imóveis, clientes e corretores
- Interface intuitiva e responsiva

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11+ com Flask
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3
- **Banco de Dados:** MySQL 8.0+
- **Bibliotecas Python:**
  - Flask (Framework web)
  - mysql-connector-python (Conector MySQL)
  - datetime (Manipulação de datas)

## 📋 Pré-requisitos

- Python 3.11 ou superior
- MySQL 8.0 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/[seu-usuario]/rent-sistema-imobiliario.git
cd rent-sistema-imobiliario
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instale as dependências:**
```bash
pip install -r requerimentts.txt
```

5. **Configure o banco de dados:**
```bash
python configurar_banco.py
```

6. **Execute a aplicação:**
```bash
python app.py
```

7. **Acesse no navegador:**
```
http://localhost:5000
```

## ⚙️ Configuração do Banco de Dados

O sistema utiliza MySQL como banco de dados. Execute o arquivo `configurar_banco.py` para criar automaticamente:

- Database `sistema_imobiliario`
- Tabelas: `clientes`, `corretores`, `imoveis`, `interesses`
- Estrutura completa com relacionamentos

## 📂 Estrutura do Projeto

```
rent-sistema-imobiliario/
├── app.py                 # Arquivo principal da aplicação
├── configurar_banco.py    # Script de configuração do banco
├── requerimentts.txt      # Dependências do projeto
├── db/
│   └── conexao.py         # Configurações de conexão com banco
├── models/
│   ├── cliente_model.py   # Modelo de dados dos clientes
│   ├── corretor_model.py  # Modelo de dados dos corretores
│   ├── imovel_model.py    # Modelo de dados dos imóveis
│   └── interesse_model.py # Modelo de dados dos interesses
├── templates/
│   ├── base.html          # Template base
│   ├── index.html         # Página inicial
│   ├── clientes/          # Templates de clientes
│   ├── corretores/        # Templates de corretores
│   ├── imoveis/           # Templates de imóveis
│   └── interesses/        # Templates de interesses
├── static/
│   ├── style.css          # Estilos CSS
│   ├── script.js          # Scripts JavaScript
│   └── imagens/           # Diretório de imagens
├── testes/                # Arquivos de teste
└── arquivos-md/           # Documentação adicional
```

## 🧪 Testes

O projeto inclui uma suite completa de testes:

```bash
# Teste do banco de dados
python testes/teste_banco.py

# Teste da API REST
python testes/teste_api_rest.py

# Teste do sistema completo
python testes/teste_sistema_completo.py

# Teste dos templates
python testes/teste_templates.py
```

## 📝 API REST

O sistema oferece endpoints REST para integração:

### Clientes
- `GET /api/clientes` - Listar todos os clientes
- `POST /api/clientes` - Criar novo cliente
- `GET /api/clientes/{id}` - Buscar cliente por ID
- `PUT /api/clientes/{id}` - Atualizar cliente
- `DELETE /api/clientes/{id}` - Remover cliente

### Imóveis
- `GET /api/imoveis` - Listar todos os imóveis
- `POST /api/imoveis` - Criar novo imóvel
- `GET /api/imoveis/{id}` - Buscar imóvel por ID
- `PUT /api/imoveis/{id}` - Atualizar imóvel
- `DELETE /api/imoveis/{id}` - Remover imóvel

### Corretores
- `GET /api/corretores` - Listar todos os corretores
- `POST /api/corretores` - Criar novo corretor
- `GET /api/corretores/{id}` - Buscar corretor por ID
- `PUT /api/corretores/{id}` - Atualizar corretor
- `DELETE /api/corretores/{id}` - Remover corretor

## 🎨 Interface

O sistema possui uma interface moderna e responsiva desenvolvida com Bootstrap 5.3, oferecendo:

- Design clean e profissional
- Navegação intuitiva
- Responsividade para dispositivos móveis
- Formulários validados
- Tabelas interativas
- Dashboard informativo

## 🔧 Configurações

### Banco de Dados
Edite o arquivo `db/conexao.py` para configurar a conexão:

```python
def obter_conexao():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='sua_senha',
        database='sistema_imobiliario'
    )
```

### Flask
Configure as variáveis de ambiente no arquivo `app.py`:

```python
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['DEBUG'] = True  # Apenas em desenvolvimento
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para o mercado imobiliário brasileiro.

## 🤝 Contribuindo

Contribuições são sempre bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## 🐛 Reportar Bugs

Encontrou um bug? Abra uma [issue](https://github.com/[seu-usuario]/rent-sistema-imobiliario/issues) e descreva:

- Passos para reproduzir o problema
- Comportamento esperado vs. atual
- Screenshots (se aplicável)
- Informações do ambiente (OS, Python, navegador)

## 📞 Suporte

Para suporte técnico ou dúvidas:

- Abra uma [issue](https://github.com/[seu-usuario]/rent-sistema-imobiliario/issues)
- Consulte a [documentação](arquivos-md/)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!