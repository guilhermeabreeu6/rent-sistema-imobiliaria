# Flask, cérebro do sistema: 

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.cliente_model import Cliente
from models.imovel_model import Imovel
from models.corretor_model import Corretor
from models.interesse_model import Interesse
from db.conexao import obter_conexao

app = Flask(__name__)
app.secret_key = 'invistta_sistema_secreto_2025'  # Necessário para flash messages

# Função de contexto para disponibilizar funções úteis nos templates
@app.context_processor
def utility_processor():
    return dict(now=datetime.now)

# Função auxiliar para determinar se a requisição quer JSON
def wants_json():
    return request.headers.get('Accept', '').find('application/json') != -1 or \
           request.headers.get('Content-Type', '').find('application/json') != -1 or \
           request.args.get('format') == 'json'

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard moderno com estatísticas do sistema"""
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)
        
        # Contar totais
        cursor.execute("SELECT COUNT(*) as total FROM clientes")
        total_clientes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM imoveis")
        total_imoveis = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM corretores")
        total_corretores = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM interesses")
        total_interesses = cursor.fetchone()['total']
        
        # Últimos clientes cadastrados
        cursor.execute("""
            SELECT nome, email, data_cadastro, id 
            FROM clientes 
            ORDER BY data_cadastro DESC 
            LIMIT 5
        """)
        clientes_recentes = cursor.fetchall()
        
        # Status dos imóveis
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM imoveis 
            GROUP BY status
        """)
        imoveis_status = cursor.fetchall()
        
        conexao.close()
        
        return render_template('index.html',
                             total_clientes=total_clientes,
                             total_imoveis=total_imoveis,
                             total_corretores=total_corretores,
                             total_interesses=total_interesses,
                             clientes_recentes=clientes_recentes,
                             imoveis_status=imoveis_status)
    except Exception as e:
        flash(f"Erro ao carregar dashboard: {e}", "error")
        return render_template('index.html',
                             total_clientes=0,
                             total_imoveis=0,
                             total_corretores=0,
                             total_interesses=0,
                             clientes_recentes=[],
                             imoveis_status=[])

# ================================
# 🌐 API REST ENDPOINTS
# ================================

# GET /clientes → Listar todos os clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    try:
        clientes = Cliente.listar_todos()
        
        # Se requisitar JSON (API), retorna JSON
        if wants_json():
            # Converter datetime para string para JSON
            clientes_json = []
            for cliente in clientes:
                cliente_copy = dict(cliente)
                if cliente_copy.get('data_cadastro'):
                    cliente_copy['data_cadastro'] = cliente_copy['data_cadastro'].isoformat()
                clientes_json.append(cliente_copy)
            
            return jsonify({
                'success': True,
                'data': clientes_json,
                'total': len(clientes_json)
            }), 200
        
        # Senão, retorna HTML (interface web simples)
        return render_template('clientes/clientes.html', clientes=clientes)
        
    except Exception as e:
        if wants_json():
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        else:
            flash(f'❌ Erro ao carregar lista de clientes: {str(e)}', 'error')
            return redirect(url_for('index'))

# POST /clientes → Criar novo cliente
@app.route('/clientes', methods=['POST'])
def criar_cliente():
    try:
        # Se é JSON (API)
        if wants_json():
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'JSON inválido'
                }), 400
                
            nome = data.get('nome', '').strip()
            email = data.get('email', '').strip()
            telefone = data.get('telefone', '').strip()
        else:
            # Se é formulário web
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            telefone = request.form.get('telefone', '').strip()

        # Validações
        if not nome:
            error_msg = 'Nome é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))
        
        if not email:
            error_msg = 'Email é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))
        
        if '@' not in email:
            error_msg = 'Email inválido!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))

        # Verificar duplicatas
        if Cliente.email_existe(email):
            error_msg = 'Este email já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))
        
        if Cliente.telefone_existe(telefone):
            error_msg = 'Este telefone já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))

        # Criar cliente
        cliente = Cliente(nome, email, telefone)
        if cliente.salvar():
            if wants_json():
                return jsonify({
                    'success': True,
                    'message': f'Cliente {nome} cadastrado com sucesso!',
                    'data': {
                        'nome': nome,
                        'email': email,
                        'telefone': telefone
                    }
                }), 201
            
            flash(f'🎉 Cliente {nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
        else:
            error_msg = 'Erro ao conectar com o banco de dados'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('cadastro'))
            
    except ValueError as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'❌ {str(e)}', 'error')
        return redirect(url_for('cadastro'))
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao cadastrar cliente: {str(e)}', 'error')
        return redirect(url_for('cadastro'))

# GET /clientes/<id> → Visualizar cliente específico
@app.route('/clientes/<int:id>', methods=['GET'])
def visualizar_cliente(id):
    try:
        cliente = Cliente.buscar_por_id(id)
        
        if not cliente:
            if wants_json():
                return jsonify({
                    'success': False,
                    'error': 'Cliente não encontrado'
                }), 404
            flash('❌ Cliente não encontrado!', 'error')
            return redirect(url_for('listar_clientes'))
        
        # Se requisitar JSON (API)
        if wants_json():
            cliente_copy = dict(cliente)
            if cliente_copy.get('data_cadastro'):
                cliente_copy['data_cadastro'] = cliente_copy['data_cadastro'].isoformat()
            
            return jsonify({
                'success': True,
                'data': cliente_copy
            }), 200
        
        # Senão, retorna HTML (interface web)
        return render_template('clientes/visualizar_cliente.html', cliente=cliente)
        
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('listar_clientes'))

# PUT /clientes/<id> → Atualizar cliente
@app.route('/clientes/<int:id>', methods=['PUT'])
def atualizar_cliente(id):
    try:
        # Verificar se cliente existe
        cliente_existente = Cliente.buscar_por_id(id)
        if not cliente_existente:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            }), 404

        # Obter dados
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON inválido'
            }), 400
            
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip()
        telefone = data.get('telefone', '').strip()

        # Validações
        if not nome:
            return jsonify({'success': False, 'error': 'Nome é obrigatório!'}), 400
        
        if not email:
            return jsonify({'success': False, 'error': 'Email é obrigatório!'}), 400
        
        if '@' not in email:
            return jsonify({'success': False, 'error': 'Email inválido!'}), 400

        # Atualizar cliente
        cliente_obj = Cliente(nome, email, telefone)
        if cliente_obj.atualizar(id):
            return jsonify({
                'success': True,
                'message': f'Cliente {nome} atualizado com sucesso!',
                'data': {
                    'id': id,
                    'nome': nome,
                    'email': email,
                    'telefone': telefone
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao atualizar cliente'
            }), 500
            
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# DELETE /clientes/<id> → Excluir cliente
@app.route('/clientes/<int:id>', methods=['DELETE'])
def excluir_cliente(id):
    try:
        # Buscar cliente para obter o nome
        cliente = Cliente.buscar_por_id(id)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            }), 404
        
        # Excluir cliente
        if Cliente.excluir(id):
            return jsonify({
                'success': True,
                'message': f'Cliente {cliente["nome"]} excluído com sucesso!'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao excluir cliente'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ================================
# 🌐 ROTAS WEB (COMPATIBILIDADE)
# ================================

# Rota para formulário de cadastro (web)
@app.route('/cadastro', methods=['GET', 'POST'])
@app.route('/clientes/adicionar', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Redireciona para o endpoint REST
        return criar_cliente()
    return render_template('clientes/cadastro_cliente.html')

# Rota para formulário de edição (web) 
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()

        # Validações básicas
        if not nome:
            flash('❌ Nome é obrigatório!', 'error')
            return redirect(url_for('editar_cliente', id=id))
        
        if not email:
            flash('❌ Email é obrigatório!', 'error')
            return redirect(url_for('editar_cliente', id=id))
        
        if '@' not in email:
            flash('❌ Email inválido!', 'error')
            return redirect(url_for('editar_cliente', id=id))

        try:
            cliente_obj = Cliente(nome, email, telefone)
            if cliente_obj.atualizar(id):
                flash(f'✏️ Cliente {nome} atualizado com sucesso!', 'success')
                return redirect(url_for('visualizar_cliente', id=id))
            else:
                flash('❌ Cliente não encontrado!', 'error')
                return redirect(url_for('listar_clientes'))
            
        except ValueError as e:
            flash(f'❌ {str(e)}', 'error')
            return redirect(url_for('editar_cliente', id=id))
        except Exception as e:
            flash(f'❌ Erro ao atualizar cliente: {str(e)}', 'error')
            return redirect(url_for('editar_cliente', id=id))
    
    # GET - Mostrar formulário de edição
    try:
        cliente = Cliente.buscar_por_id(id)
        if cliente:
            return render_template('clientes/editar_cliente.html', cliente=cliente)
        else:
            flash('❌ Cliente não encontrado!', 'error')
            return redirect(url_for('listar_clientes'))
    except Exception as e:
        flash(f'❌ Erro ao carregar cliente: {str(e)}', 'error')
        return redirect(url_for('listar_clientes'))

# Rota de exclusão para web (compatibilidade)
@app.route('/clientes/delete/<int:id>')
def deletar_cliente_web(id):
    try:
        cliente = Cliente.buscar_por_id(id)
        
        if cliente and Cliente.excluir(id):
            flash(f'🗑️ Cliente {cliente["nome"]} excluído com sucesso!', 'success')
        else:
            flash('❌ Cliente não encontrado!', 'error')
            
    except Exception as e:
        flash(f'❌ Erro ao excluir cliente: {str(e)}', 'error')
        
    return redirect(url_for('listar_clientes'))

# ================================
# 📚 DOCUMENTAÇÃO E UTILITÁRIOS
# ================================

# Rota para documentação da API
@app.route('/api/docs')
def api_docs():
    docs = {
        "title": "Invistta Sistema - API REST",
        "version": "1.0.0",
        "description": "API completa para gerenciamento de clientes",
        "endpoints": {
            "clientes": {
                "GET /clientes": {
                    "description": "Lista todos os clientes",
                    "parameters": {
                        "format": "Opcional. Use 'json' para resposta JSON"
                    },
                    "responses": {
                        "200": "Lista de clientes",
                        "500": "Erro interno"
                    }
                },
                "POST /clientes": {
                    "description": "Cria um novo cliente",
                    "body": {
                        "nome": "string (obrigatório)",
                        "email": "string (obrigatório, único)",
                        "telefone": "string (opcional, único)"
                    },
                    "responses": {
                        "201": "Cliente criado",
                        "400": "Dados inválidos",
                        "409": "Email/telefone já existe"
                    }
                },
                "GET /clientes/:id": {
                    "description": "Busca um cliente específico",
                    "responses": {
                        "200": "Dados do cliente",
                        "404": "Cliente não encontrado"
                    }
                },
                "PUT /clientes/:id": {
                    "description": "Atualiza um cliente",
                    "body": {
                        "nome": "string (obrigatório)",
                        "email": "string (obrigatório)",
                        "telefone": "string (opcional)"
                    },
                    "responses": {
                        "200": "Cliente atualizado",
                        "400": "Dados inválidos",
                        "404": "Cliente não encontrado"
                    }
                },
                "DELETE /clientes/:id": {
                    "description": "Exclui um cliente",
                    "responses": {
                        "200": "Cliente excluído",
                        "404": "Cliente não encontrado"
                    }
                }
            }
        },
        "examples": {
            "create_client": {
                "method": "POST",
                "url": "/clientes",
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "nome": "João Silva",
                    "email": "joao@email.com",
                    "telefone": "(11) 99999-9999"
                }
            }
        }
    }
    
    if wants_json():
        return jsonify(docs)
    
    return "<h1>API Documentation</h1><pre>" + str(docs) + "</pre>"

# Rota para testar mensagens (opcional - pode remover depois)
@app.route('/teste-mensagens')
def teste_mensagens():
    flash('🎉 Mensagem de sucesso!', 'success')
    flash('❌ Mensagem de erro!', 'error') 
    flash('ℹ️ Mensagem informativa!', 'info')
    return redirect(url_for('index'))

# ================================
# 👨‍💼 ROTAS DE CORRETORES - CRUD COMPLETO
# ================================

# GET /corretores → Listar todos os corretores
@app.route('/corretores', methods=['GET'])
def listar_corretores():
    try:
        corretores = Corretor.listar_todos()
        estatisticas = Corretor.contar_estatisticas()
        
        # Se requisitar JSON (API), retorna JSON
        if wants_json():
            # Converter datetime para string para JSON
            corretores_json = []
            for corretor in corretores:
                corretor_copy = dict(corretor)
                if corretor_copy.get('data_cadastro'):
                    corretor_copy['data_cadastro'] = corretor_copy['data_cadastro'].isoformat()
                corretores_json.append(corretor_copy)
            
            return jsonify({
                'success': True,
                'data': corretores_json,
                'total': len(corretores_json),
                'estatisticas': estatisticas
            }), 200
        
        # Senão, retorna HTML (interface web)
        return render_template('corretores/listar.html', 
                             corretores=corretores, 
                             estatisticas=estatisticas)
        
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao carregar corretores: {str(e)}', 'error')
        return redirect(url_for('index'))

# GET/POST /corretores/adicionar → Cadastrar novo corretor
@app.route('/corretores/adicionar', methods=['GET', 'POST'])
def adicionar_corretor():
    if request.method == 'GET':
        return render_template('corretores/cadastrar.html')
    
    # POST - Processar cadastro
    try:
        # Capturar dados do formulário ou JSON
        if wants_json():
            data = request.get_json()
        else:
            data = request.form
        
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip()
        telefone = data.get('telefone', '').strip()
        creci = data.get('creci', '').strip()
        
        # Validações básicas
        if not nome:
            error_msg = 'Nome é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        if not email:
            error_msg = 'Email é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        # Validar formato do email
        if not Corretor.validar_email(email):
            error_msg = 'Email inválido!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        # Verificar se email já existe
        if Corretor.email_existe(email):
            error_msg = 'Este email já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        # Validar CRECI se fornecido
        if creci and not Corretor.validar_creci(creci):
            error_msg = 'CRECI inválido! Use formato: CRECI-12345 ou CRECI/TO 12345'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        # Verificar se CRECI já existe
        if creci and Corretor.creci_existe(creci):
            error_msg = 'Este CRECI já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
        
        # Criar corretor
        corretor = Corretor(nome, email, telefone or None, creci or None)
        if corretor.salvar():
            success_msg = f'Corretor {nome} cadastrado com sucesso!'
            if wants_json():
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'data': {
                        'id': corretor.id,
                        'nome': nome,
                        'email': email,
                        'telefone': telefone,
                        'creci': creci
                    }
                }), 201
            
            flash(f'👨‍💼 {success_msg}', 'success')
            return redirect(url_for('listar_corretores'))
        else:
            error_msg = 'Erro ao conectar com o banco de dados'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_corretor'))
            
    except ValueError as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'❌ {str(e)}', 'error')
        return redirect(url_for('adicionar_corretor'))
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao cadastrar corretor: {str(e)}', 'error')
        return redirect(url_for('adicionar_corretor'))

# GET/POST /corretores/<id>/editar → Editar corretor
@app.route('/corretores/<int:id>/editar', methods=['GET', 'POST'])
def editar_corretor(id):
    if request.method == 'GET':
        # Carregar corretor
        corretor = Corretor.buscar_por_id(id)
        if not corretor:
            flash('❌ Corretor não encontrado!', 'error')
            return redirect(url_for('listar_corretores'))
        
        return render_template('corretores/editar.html', corretor=corretor)
    
    # POST - Processar atualização
    return _processar_atualizacao_corretor(id)

# PUT /corretores/<id> → Atualizar corretor via API REST
@app.route('/corretores/<int:id>', methods=['PUT'])
def atualizar_corretor_api(id):
    return _processar_atualizacao_corretor(id)

def _processar_atualizacao_corretor(id):
    try:
        # Verificar se corretor existe
        corretor_existente = Corretor.buscar_por_id(id)
        if not corretor_existente:
            if wants_json():
                return jsonify({'success': False, 'error': 'Corretor não encontrado'}), 404
            flash('❌ Corretor não encontrado!', 'error')
            return redirect(url_for('listar_corretores'))
        
        # Capturar dados
        if wants_json():
            data = request.get_json()
        else:
            data = request.form
        
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip()
        telefone = data.get('telefone', '').strip()
        creci = data.get('creci', '').strip()
        
        # Validações
        if not nome or not email:
            error_msg = 'Nome e email são obrigatórios!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
        
        # Validar formato do email
        if not Corretor.validar_email(email):
            error_msg = 'Email inválido!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
        
        # Verificar email duplicado (excluindo o próprio)
        if Corretor.email_existe(email, id):
            error_msg = 'Este email já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
        
        # Validar CRECI
        if creci and not Corretor.validar_creci(creci):
            error_msg = 'CRECI inválido!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
        
        # Verificar CRECI duplicado (excluindo o próprio)
        if creci and Corretor.creci_existe(creci, id):
            error_msg = 'Este CRECI já está cadastrado!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 409
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
        
        # Atualizar corretor
        corretor = Corretor(nome, email, telefone or None, creci or None)
        if corretor.atualizar(id):
            success_msg = f'Corretor {nome} atualizado com sucesso!'
            if wants_json():
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'data': {
                        'id': id,
                        'nome': nome,
                        'email': email,
                        'telefone': telefone,
                        'creci': creci
                    }
                }), 200
            
            flash(f'✅ {success_msg}', 'success')
            return redirect(url_for('listar_corretores'))
        else:
            error_msg = 'Erro ao atualizar corretor'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_corretor', id=id))
            
    except ValueError as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'❌ {str(e)}', 'error')
        return redirect(url_for('editar_corretor', id=id))
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao atualizar corretor: {str(e)}', 'error')
        return redirect(url_for('editar_corretor', id=id))

# GET /corretores/<id>/excluir → Excluir corretor
@app.route('/corretores/<int:id>/excluir')
def excluir_corretor(id):
    try:
        corretor = Corretor.buscar_por_id(id)
        
        if corretor:
            if Corretor.excluir(id):
                flash(f'🗑️ Corretor {corretor["nome"]} excluído com sucesso!', 'success')
            else:
                flash('❌ Erro ao excluir corretor!', 'error')
        else:
            flash('❌ Corretor não encontrado!', 'error')
            
    except ValueError as e:
        flash(f'❌ {str(e)}', 'error')
    except Exception as e:
        flash(f'❌ Erro ao excluir corretor: {str(e)}', 'error')
        
    return redirect(url_for('listar_corretores'))

# DELETE /corretores/<id> → Excluir corretor via API REST
@app.route('/corretores/<int:id>', methods=['DELETE'])
def excluir_corretor_api(id):
    try:
        corretor = Corretor.buscar_por_id(id)
        
        if not corretor:
            return jsonify({
                'success': False,
                'error': 'Corretor não encontrado'
            }), 404
        
        if Corretor.excluir(id):
            return jsonify({
                'success': True,
                'message': f'Corretor {corretor["nome"]} excluído com sucesso!'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao excluir corretor'
            }), 500
            
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# GET /corretores/<id> → Visualizar corretor específico
@app.route('/corretores/<int:id>')
def visualizar_corretor(id):
    try:
        corretor = Corretor.buscar_por_id(id)
        
        if not corretor:
            if wants_json():
                return jsonify({'success': False, 'error': 'Corretor não encontrado'}), 404
            flash('❌ Corretor não encontrado!', 'error')
            return redirect(url_for('listar_corretores'))
        
        # Se requisitar JSON (API)
        if wants_json():
            corretor_copy = dict(corretor)
            if corretor_copy.get('data_cadastro'):
                corretor_copy['data_cadastro'] = corretor_copy['data_cadastro'].isoformat()
            
            # Adicionar lista de imóveis
            imoveis = Corretor.buscar_imoveis_do_corretor(id)
            for imovel in imoveis:
                if imovel.get('data_cadastro'):
                    imovel['data_cadastro'] = imovel['data_cadastro'].isoformat()
            
            return jsonify({
                'success': True,
                'data': {
                    'corretor': corretor_copy,
                    'imoveis': imoveis
                }
            }), 200
        
        # Senão, retorna HTML (interface web) - buscar imóveis para exibir
        imoveis = Corretor.buscar_imoveis_do_corretor(id)
        return render_template('corretores/visualizar.html', 
                             corretor=corretor, 
                             imoveis=imoveis)
        
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao carregar corretor: {str(e)}', 'error')
        return redirect(url_for('listar_corretores'))

# ================================
# 🏠 ROTAS DE IMÓVEIS - CRUD COMPLETO
# ================================

# GET /imoveis → Listar todos os imóveis
@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    try:
        imoveis = Imovel.listar_todos()
        
        # Se requisitar JSON (API), retorna JSON
        if wants_json():
            # Converter datetime para string para JSON
            imoveis_json = []
            for imovel in imoveis:
                imovel_copy = dict(imovel)
                if imovel_copy.get('data_cadastro'):
                    imovel_copy['data_cadastro'] = imovel_copy['data_cadastro'].isoformat()
                imoveis_json.append(imovel_copy)
            
            return jsonify({
                'success': True,
                'data': imoveis_json,
                'total': len(imoveis_json)
            }), 200
        
        # Senão, retorna HTML (interface web)
        estatisticas = Imovel.contar_por_status()
        return render_template('imoveis/listar.html', imoveis=imoveis, estatisticas=estatisticas)
        
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao carregar imóveis: {str(e)}', 'error')
        return redirect(url_for('index'))

# GET/POST /imoveis/adicionar → Cadastrar novo imóvel
@app.route('/imoveis/adicionar', methods=['GET', 'POST'])
def adicionar_imovel():
    if request.method == 'GET':
        # Carregar lista de corretores para o formulário
        corretores = Imovel.listar_corretores()
        return render_template('imoveis/cadastar.html', corretores=corretores)
    
    # POST - Processar cadastro
    try:
        # Capturar dados do formulário ou JSON
        if wants_json():
            data = request.get_json()
        else:
            data = request.form
        
        tipo = data.get('tipo', '').strip()
        endereco = data.get('endereco', '').strip()
        valor = data.get('valor', '')
        if isinstance(valor, str):
            valor = valor.strip()
        status = data.get('status', 'disponível')
        corretor_id = data.get('corretor_id')
        
        # Validações básicas
        if not tipo:
            error_msg = 'Tipo do imóvel é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_imovel'))
        
        if not endereco:
            error_msg = 'Endereço é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_imovel'))
        
        if not valor:
            error_msg = 'Valor é obrigatório!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_imovel'))
        
        try:
            if isinstance(valor, (int, float)):
                valor_float = float(valor)
            else:
                valor_float = float(str(valor).replace(',', '.'))
            if valor_float <= 0:
                raise ValueError("Valor deve ser maior que zero")
        except ValueError:
            error_msg = 'Valor inválido! Use apenas números.'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_imovel'))
        
        # Validar corretor_id se fornecido
        if corretor_id and corretor_id != '':
            try:
                corretor_id = int(corretor_id)
            except ValueError:
                corretor_id = None
        else:
            corretor_id = None
        
        # Criar imóvel
        imovel = Imovel(tipo, endereco, valor_float, status, corretor_id)
        if imovel.salvar():
            success_msg = f'Imóvel {tipo} cadastrado com sucesso!'
            if wants_json():
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'data': {
                        'id': imovel.id,
                        'tipo': tipo,
                        'endereco': endereco,
                        'valor': valor_float,
                        'status': status
                    }
                }), 201
            
            flash(f'🏠 {success_msg}', 'success')
            return redirect(url_for('listar_imoveis'))
        else:
            error_msg = 'Erro ao conectar com o banco de dados'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('adicionar_imovel'))
            
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao cadastrar imóvel: {str(e)}', 'error')
        return redirect(url_for('adicionar_imovel'))

# GET/POST /imoveis/<id>/editar → Editar imóvel
@app.route('/imoveis/<int:id>/editar', methods=['GET', 'POST'])
def editar_imovel(id):
    if request.method == 'GET':
        # Carregar imóvel e corretores
        imovel = Imovel.buscar_por_id(id)
        if not imovel:
            flash('❌ Imóvel não encontrado!', 'error')
            return redirect(url_for('listar_imoveis'))
        
        corretores = Imovel.listar_corretores()
        return render_template('imoveis/editar.html', imovel=imovel, corretores=corretores)
    
    # POST - Processar atualização
    return _processar_atualizacao_imovel(id)

# PUT /imoveis/<id> → Atualizar imóvel via API REST
@app.route('/imoveis/<int:id>', methods=['PUT'])
def atualizar_imovel_api(id):
    return _processar_atualizacao_imovel(id)

def _processar_atualizacao_imovel(id):
    try:
        # Verificar se imóvel existe
        imovel_existente = Imovel.buscar_por_id(id)
        if not imovel_existente:
            if wants_json():
                return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404
            flash('❌ Imóvel não encontrado!', 'error')
            return redirect(url_for('listar_imoveis'))
        
        # Capturar dados
        if wants_json():
            data = request.get_json()
        else:
            data = request.form
        
        tipo = data.get('tipo', '').strip()
        endereco = data.get('endereco', '').strip()
        valor = data.get('valor', '').strip()
        status = data.get('status', 'disponível')
        corretor_id = data.get('corretor_id')
        
        # Validações (mesmo que no cadastro)
        if not tipo or not endereco or not valor:
            error_msg = 'Todos os campos obrigatórios devem ser preenchidos!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_imovel', id=id))
        
        try:
            valor_float = float(valor.replace(',', '.'))
            if valor_float <= 0:
                raise ValueError("Valor deve ser maior que zero")
        except ValueError:
            error_msg = 'Valor inválido!'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_imovel', id=id))
        
        # Validar corretor_id
        if corretor_id and corretor_id != '':
            try:
                corretor_id = int(corretor_id)
            except ValueError:
                corretor_id = None
        else:
            corretor_id = None
        
        # Atualizar imóvel
        imovel = Imovel(tipo, endereco, valor_float, status, corretor_id)
        if imovel.atualizar(id):
            success_msg = f'Imóvel {tipo} atualizado com sucesso!'
            if wants_json():
                return jsonify({
                    'success': True,
                    'message': success_msg,
                    'data': {
                        'id': id,
                        'tipo': tipo,
                        'endereco': endereco,
                        'valor': valor_float,
                        'status': status
                    }
                }), 200
            
            flash(f'✅ {success_msg}', 'success')
            return redirect(url_for('listar_imoveis'))
        else:
            error_msg = 'Erro ao atualizar imóvel'
            if wants_json():
                return jsonify({'success': False, 'error': error_msg}), 500
            flash(f'❌ {error_msg}', 'error')
            return redirect(url_for('editar_imovel', id=id))
            
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao atualizar imóvel: {str(e)}', 'error')
        return redirect(url_for('editar_imovel', id=id))

# GET /imoveis/<id>/excluir → Excluir imóvel
@app.route('/imoveis/<int:id>/excluir')
def excluir_imovel(id):
    try:
        imovel = Imovel.buscar_por_id(id)
        
        if imovel and Imovel.excluir(id):
            flash(f'🗑️ Imóvel {imovel["tipo"]} excluído com sucesso!', 'success')
        else:
            flash('❌ Imóvel não encontrado!', 'error')
            
    except Exception as e:
        flash(f'❌ Erro ao excluir imóvel: {str(e)}', 'error')
        
    return redirect(url_for('listar_imoveis'))

# GET /imoveis/<id> → Visualizar imóvel específico
@app.route('/imoveis/<int:id>')
def visualizar_imovel(id):
    try:
        imovel = Imovel.buscar_por_id(id)
        
        if not imovel:
            if wants_json():
                return jsonify({'success': False, 'error': 'Imóvel não encontrado'}), 404
            flash('❌ Imóvel não encontrado!', 'error')
            return redirect(url_for('listar_imoveis'))
        
        # Se requisitar JSON (API)
        if wants_json():
            imovel_copy = dict(imovel)
            if imovel_copy.get('data_cadastro'):
                imovel_copy['data_cadastro'] = imovel_copy['data_cadastro'].isoformat()
            
            return jsonify({
                'success': True,
                'data': imovel_copy
            }), 200
        
        # Senão, retorna HTML (interface web)
        return render_template('imoveis/visualizar.html', imovel=imovel)
        
    except Exception as e:
        if wants_json():
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'❌ Erro ao carregar imóvel: {str(e)}', 'error')
        return redirect(url_for('listar_imoveis'))
    

# CRUD DE INTERESSES (CLIENTES <> IMÓVEIS)
# Listar interesses
@app.route("/interesses")
def listar_interesses():
    interesses = Interesse.listar_todos()
    return render_template("interesses/interesses.html", interesses=interesses)

# Adicionar novo interesse
@app.route("/interesse/add", methods=["GET", "POST"])
@app.route("/interesses/adicionar", methods=["GET", "POST"])
def adicionar_interesse():
    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        imovel_id = request.form["imovel_id"]
        status = request.form.get("status", "Ativo")
        data_interesse = request.form.get("data_interesse")
        observacoes = request.form.get("observacoes")

        # Converter data_interesse se necessário
        if data_interesse:
            data_interesse = datetime.strptime(data_interesse, '%Y-%m-%dT%H:%M')

        interesse = Interesse(cliente_id, imovel_id, status, data_interesse, observacoes)
        interesse.salvar()
        flash("Interesse registrado com sucesso!", "success")
        return redirect("/interesses")
    
    # Pega os clientes e imóveis disponíveis (para dropdown)
    conexao = obter_conexao()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome")
    clientes = cursor.fetchall()
    cursor.execute("SELECT id, tipo, endereco, valor FROM imoveis ORDER BY tipo, endereco")
    imoveis = cursor.fetchall()
    conexao.close()

    # Data/hora atual para valor padrão
    data_atual = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    return render_template("interesses/adicionar_interesse.html", 
                         clientes=clientes, 
                         imoveis=imoveis, 
                         data_atual=data_atual)

# Atualizar status do interesse
@app.route("/interesse/<int:id>/editar", methods=["POST"])
def atualizar_interesse(id):
    novo_status = request.form["status"]
    Interesse.atualizar_status(id, novo_status)
    flash("Status do interesse atualizado com sucesso!", "success")
    return redirect("/interesses")

# Visualizar interesse
@app.route("/interesse/<int:id>")
@app.route("/interesses/<int:id>")
def visualizar_interesse(id):
    interesse = Interesse.buscar_por_id(id)
    if not interesse:
        flash("Interesse não encontrado!", "error")
        return redirect("/interesses")
    return render_template("interesses/visualizar_interesse.html", interesse=interesse)

# Deletar interesse
@app.route("/interesse/<int:id>/delete")
@app.route("/interesses/<int:id>/remover")
def deletar_interesse(id):
    Interesse.deletar(id)
    flash("Interesse removido com sucesso!", "success")
    return redirect("/interesses")


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'OK',
        'service': 'Invistta Sistema',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    app.run(debug = True)