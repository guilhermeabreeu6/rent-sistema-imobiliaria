"""Aplicação Flask para o sistema RENT usando armazenamento em memória."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from db.storage import Record, repo
from models.cliente_model import Cliente
from models.corretor_model import Corretor
from models.imovel_model import Imovel
from models.interesse_model import Interesse

app = Flask(__name__)
app.secret_key = "rent-demo-secret"


@app.context_processor
def inject_now():
    return {"now": datetime.utcnow}


def wants_json() -> bool:
    accept = request.headers.get("Accept", "")
    content_type = request.headers.get("Content-Type", "")
    return (
        "application/json" in accept
        or "application/json" in content_type
        or request.args.get("format") == "json"
    )


def _serialize_record(record: Optional[Record]) -> Optional[Dict]:
    if record is None:
        return None
    if hasattr(record, "to_serializable"):
        return record.to_serializable()
    data = dict(record)
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data


def _serialize_records(records: List[Record]) -> List[Dict]:
    return [_serialize_record(record) for record in records]


@app.route("/")
def index():
    return dashboard()


@app.route("/dashboard")
def dashboard():
    clientes = Cliente.listar_todos()
    imoveis = Imovel.listar_todos()
    corretores = Corretor.listar_todos()
    interesses = Interesse.listar_todos()

    imoveis_status: Dict[str, int] = {}
    for imovel in imoveis:
        status = imovel.get("status", "desconhecido")
        imoveis_status[status] = imoveis_status.get(status, 0) + 1

    clientes_recentes = sorted(clientes, key=lambda c: c.get("data_cadastro"), reverse=True)[:5]

    return render_template(
        "index.html",
        total_clientes=len(clientes),
        total_imoveis=len(imoveis),
        total_corretores=len(corretores),
        total_interesses=len(interesses),
        clientes_recentes=clientes_recentes,
        imoveis_status=[{"status": k, "count": v} for k, v in imoveis_status.items()],
    )


@app.route("/health")
def health():
    return jsonify({"status": "OK", "service": "RENT", "version": "2.0.0"})


@app.route("/api/docs")
def api_docs():
    docs = {
        "title": "RENT API",
        "version": "2.0.0",
        "endpoints": {
            "clientes": {
                "list": "GET /clientes",
                "create": "POST /clientes",
                "detail": "GET /clientes/<id>",
                "update": "PUT /clientes/<id>",
                "delete": "DELETE /clientes/<id>",
            },
            "corretores": {
                "list": "GET /corretores",
                "create": "POST /corretores/adicionar",
                "detail": "GET /corretores/<id>",
                "update": "PUT /corretores/<id>",
            },
            "imoveis": {
                "list": "GET /imoveis",
                "create": "POST /imoveis/adicionar",
                "detail": "GET /imoveis/<id>",
                "update": "PUT /imoveis/<id>",
            },
            "interesses": {
                "list": "GET /interesses",
                "create": "POST /interesses/adicionar",
            },
        },
    }
    return jsonify(docs)


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------


def _obter_dados_cliente(origem: str) -> Dict[str, str]:
    if origem == "json":
        data = request.get_json(silent=True) or {}
        return {
            "nome": data.get("nome", "").strip(),
            "email": data.get("email", "").strip(),
            "telefone": data.get("telefone", "").strip(),
            "endereco": data.get("endereco"),
        }
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "telefone": request.form.get("telefone", "").strip(),
        "endereco": request.form.get("endereco", "").strip() or None,
    }


@app.route("/clientes", methods=["GET"])
def listar_clientes():
    clientes = Cliente.listar_todos()
    if wants_json():
        dados = _serialize_records(clientes)
        return jsonify({"success": True, "data": dados, "total": len(dados)})
    return render_template("clientes/clientes.html", clientes=clientes)


@app.route("/clientes", methods=["POST"])
def criar_cliente():
    origem = "json" if wants_json() else "form"
    dados = _obter_dados_cliente(origem)

    if not dados["nome"]:
        mensagem = "Nome é obrigatório"
        if origem == "json":
            return jsonify({"success": False, "error": mensagem}), 400
        flash(f"❌ {mensagem}", "error")
        return redirect(url_for("cadastro"))

    if not dados["email"] or "@" not in dados["email"]:
        mensagem = "Email inválido"
        if origem == "json":
            return jsonify({"success": False, "error": mensagem}), 400
        flash(f"❌ {mensagem}", "error")
        return redirect(url_for("cadastro"))

    try:
        cliente = Cliente(**dados)
        cliente.salvar()
    except ValueError as exc:
        if origem == "json":
            resposta = jsonify({"success": False, "error": str(exc)})
            resposta.status_code = 409
            return resposta
        flash(f"❌ {exc}", "error")
        return redirect(url_for("cadastro"))

    if origem == "json":
        resposta = jsonify(
            {
                "success": True,
                "message": f"Cliente {dados['nome']} cadastrado com sucesso!",
                "data": dados,
            }
        )
        resposta.status_code = 201
        return resposta

    flash(f"🎉 Cliente {dados['nome']} cadastrado com sucesso!", "success")
    return redirect(url_for("listar_clientes"))


@app.route("/clientes/<int:cliente_id>", methods=["GET"])
def visualizar_cliente(cliente_id: int):
    cliente = Cliente.buscar_por_id(cliente_id)
    if not cliente:
        if wants_json():
            return jsonify({"success": False, "error": "Cliente não encontrado"}), 404
        flash("❌ Cliente não encontrado!", "error")
        return redirect(url_for("listar_clientes"))

    interesses = Cliente.listar_interesses(cliente_id)

    if wants_json():
        dados = _serialize_record(cliente)
        dados["interesses"] = _serialize_records(interesses)
        return jsonify({"success": True, "data": dados})

    return render_template(
        "clientes/visualizar_cliente.html",
        cliente=cliente,
        interesses=interesses,
    )


@app.route("/clientes/<int:cliente_id>", methods=["PUT"])
def atualizar_cliente(cliente_id: int):
    dados = _obter_dados_cliente("json")
    if not dados["nome"]:
        return jsonify({"success": False, "error": "Nome é obrigatório"}), 400
    if not dados["email"] or "@" not in dados["email"]:
        return jsonify({"success": False, "error": "Email inválido"}), 400

    try:
        cliente = Cliente(**dados)
        cliente.atualizar(cliente_id)
    except ValueError as exc:
        resposta = jsonify({"success": False, "error": str(exc)})
        resposta.status_code = 409
        return resposta
    except KeyError:
        return jsonify({"success": False, "error": "Cliente não encontrado"}), 404

    resposta = dados.copy()
    resposta["id"] = cliente_id
    return jsonify({"success": True, "message": "Cliente atualizado com sucesso", "data": resposta})


@app.route("/clientes/<int:cliente_id>", methods=["DELETE"])
def excluir_cliente(cliente_id: int):
    if not Cliente.excluir(cliente_id):
        return jsonify({"success": False, "error": "Cliente não encontrado"}), 404
    return jsonify({"success": True, "message": "Cliente excluído com sucesso"})


@app.route("/clientes/<int:cliente_id>/delete")
def deletar_cliente_web(cliente_id: int):
    if Cliente.excluir(cliente_id):
        flash("Cliente removido com sucesso!", "success")
    else:
        flash("Cliente não encontrado!", "error")
    return redirect(url_for("listar_clientes"))


@app.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id: int):
    cliente = Cliente.buscar_por_id(cliente_id)
    if not cliente:
        flash("❌ Cliente não encontrado!", "error")
        return redirect(url_for("listar_clientes"))

    if request.method == "POST":
        dados = _obter_dados_cliente("form")
        if not dados["nome"] or not dados["email"]:
            flash("❌ Nome e email são obrigatórios!", "error")
            return redirect(url_for("editar_cliente", cliente_id=cliente_id))
        try:
            Cliente(**dados).atualizar(cliente_id)
        except ValueError as exc:
            flash(f"❌ {exc}", "error")
            return redirect(url_for("editar_cliente", cliente_id=cliente_id))
        flash("✏️ Cliente atualizado com sucesso!", "success")
        return redirect(url_for("visualizar_cliente", cliente_id=cliente_id))

    return render_template("clientes/editar_cliente.html", cliente=cliente)


@app.route("/cadastro")
@app.route("/clientes/adicionar")
@app.route("/clientes/novo")
def cadastro():
    return render_template("clientes/cadastro_cliente.html")


# ---------------------------------------------------------------------------
# Corretores
# ---------------------------------------------------------------------------

def _serialize_corretor(corretor: Record) -> Dict:
    dados = _serialize_record(corretor)
    dados["total_imoveis"] = len(Corretor.listar_imoveis(corretor["id"]))
    return dados


@app.route("/corretores", methods=["GET"])
def listar_corretores():
    corretores = Corretor.listar_todos()
    if wants_json():
        estatisticas = Corretor.estatisticas()
        return jsonify(
            {
                "success": True,
                "data": [_serialize_corretor(c) for c in corretores],
                "total": len(corretores),
                "estatisticas": {
                    "total_corretores": estatisticas.total_corretores,
                    "corretores_ativos": estatisticas.corretores_ativos,
                    "total_imoveis": estatisticas.total_imoveis,
                    "imoveis_por_status": estatisticas.imoveis_por_status,
                },
            }
        )
    return render_template("corretores/listar.html", corretores=corretores)


def _dados_corretor(origem: str) -> Dict[str, str]:
    if origem == "json":
        data = request.get_json(silent=True) or {}
        return {
            "nome": data.get("nome", "").strip(),
            "email": data.get("email", "").strip(),
            "telefone": data.get("telefone", "").strip(),
            "creci": data.get("creci", "").strip() or None,
        }
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "telefone": request.form.get("telefone", "").strip(),
        "creci": request.form.get("creci", "").strip() or None,
    }


@app.route("/corretores/adicionar", methods=["GET", "POST"])
def adicionar_corretor():
    if request.method == "GET":
        return render_template("corretores/cadastrar.html")

    origem = "json" if wants_json() else "form"
    dados = _dados_corretor(origem)

    if not dados["nome"] or not dados["email"]:
        mensagem = "Nome e email são obrigatórios"
        if origem == "json":
            return jsonify({"success": False, "error": mensagem}), 400
        flash(f"❌ {mensagem}", "error")
        return redirect(url_for("adicionar_corretor"))

    try:
        Corretor(**dados).salvar()
    except ValueError as exc:
        if origem == "json":
            resposta = jsonify({"success": False, "error": str(exc)})
            resposta.status_code = 409
            return resposta
        flash(f"❌ {exc}", "error")
        return redirect(url_for("adicionar_corretor"))

    if origem == "json":
        corretor = Corretor.listar_todos()[-1]
        resposta = jsonify({"success": True, "message": "Corretor cadastrado", "data": _serialize_corretor(corretor)})
        resposta.status_code = 201
        return resposta

    flash("🎉 Corretor cadastrado com sucesso!", "success")
    return redirect(url_for("listar_corretores"))


@app.route("/corretores/<int:corretor_id>", methods=["GET"])
def visualizar_corretor(corretor_id: int):
    corretor = Corretor.buscar_por_id(corretor_id)
    if not corretor:
        if wants_json():
            return jsonify({"success": False, "error": "Corretor não encontrado"}), 404
        flash("❌ Corretor não encontrado!", "error")
        return redirect(url_for("listar_corretores"))

    imoveis = Corretor.listar_imoveis(corretor_id)

    if wants_json():
        return jsonify(
            {
                "success": True,
                "data": {
                    "corretor": _serialize_corretor(corretor),
                    "imoveis": _serialize_records(imoveis),
                },
            }
        )

    return render_template(
        "corretores/visualizar.html",
        corretor=corretor,
        imoveis=imoveis,
    )


@app.route("/corretores/<int:corretor_id>", methods=["PUT"])
def atualizar_corretor(corretor_id: int):
    dados = _dados_corretor("json")
    if not dados["nome"] or not dados["email"]:
        return jsonify({"success": False, "error": "Nome e email são obrigatórios"}), 400
    try:
        Corretor(**dados).atualizar(corretor_id)
    except ValueError as exc:
        resposta = jsonify({"success": False, "error": str(exc)})
        resposta.status_code = 409
        return resposta
    except KeyError:
        return jsonify({"success": False, "error": "Corretor não encontrado"}), 404

    resposta = _serialize_corretor(Corretor.buscar_por_id(corretor_id))
    return jsonify({"success": True, "message": "Corretor atualizado com sucesso", "data": resposta})


@app.route("/corretores/<int:corretor_id>/editar", methods=["GET", "POST"])
def editar_corretor(corretor_id: int):
    corretor = Corretor.buscar_por_id(corretor_id)
    if not corretor:
        flash("❌ Corretor não encontrado!", "error")
        return redirect(url_for("listar_corretores"))

    if request.method == "POST":
        dados = _dados_corretor("form")
        if not dados["nome"] or not dados["email"]:
            flash("❌ Nome e email são obrigatórios!", "error")
            return redirect(url_for("editar_corretor", corretor_id=corretor_id))
        try:
            Corretor(**dados).atualizar(corretor_id)
        except ValueError as exc:
            flash(f"❌ {exc}", "error")
            return redirect(url_for("editar_corretor", corretor_id=corretor_id))
        flash("✏️ Corretor atualizado com sucesso!", "success")
        return redirect(url_for("visualizar_corretor", corretor_id=corretor_id))

    return render_template("corretores/editar.html", corretor=corretor)


# ---------------------------------------------------------------------------
# Imóveis
# ---------------------------------------------------------------------------

def _dados_imovel(origem: str) -> Dict:
    if origem == "json":
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
    return {
        "tipo": (data.get("tipo") or "").strip(),
        "endereco": (data.get("endereco") or "").strip(),
        "valor": float(data.get("valor", 0) or 0),
        "status": (data.get("status") or "disponivel").strip(),
        "corretor_id": int(data.get("corretor_id")) if data.get("corretor_id") else None,
        "descricao": (data.get("descricao") or None),
    }


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    imoveis = Imovel.listar_todos()
    if wants_json():
        return jsonify({"success": True, "data": _serialize_records(imoveis), "total": len(imoveis)})
    return render_template("imoveis/listar.html", imoveis=imoveis)


@app.route("/imoveis/adicionar", methods=["GET", "POST"])
def adicionar_imovel():
    if request.method == "GET":
        return render_template("imoveis/cadastrar.html", corretores=Corretor.listar_todos())

    origem = "json" if wants_json() else "form"
    dados = _dados_imovel(origem)

    if not dados["tipo"] or not dados["endereco"]:
        mensagem = "Tipo e endereço são obrigatórios"
        if origem == "json":
            return jsonify({"success": False, "error": mensagem}), 400
        flash(f"❌ {mensagem}", "error")
        return redirect(url_for("adicionar_imovel"))

    try:
        Imovel(**dados).salvar()
    except ValueError as exc:
        if origem == "json":
            return jsonify({"success": False, "error": str(exc)}), 400
        flash(f"❌ {exc}", "error")
        return redirect(url_for("adicionar_imovel"))

    if origem == "json":
        imovel = Imovel.listar_todos()[-1]
        resposta = jsonify({"success": True, "message": "Imóvel cadastrado", "data": _serialize_record(imovel)})
        resposta.status_code = 201
        return resposta

    flash("🏠 Imóvel cadastrado com sucesso!", "success")
    return redirect(url_for("listar_imoveis"))


@app.route("/imoveis/<int:imovel_id>", methods=["GET"])
def visualizar_imovel(imovel_id: int):
    imovel = Imovel.buscar_por_id(imovel_id)
    if not imovel:
        if wants_json():
            return jsonify({"success": False, "error": "Imóvel não encontrado"}), 404
        flash("❌ Imóvel não encontrado!", "error")
        return redirect(url_for("listar_imoveis"))

    corretor = Corretor.buscar_por_id(imovel.get("corretor_id")) if imovel.get("corretor_id") else None

    if wants_json():
        dados = _serialize_record(imovel)
        dados["corretor"] = _serialize_record(corretor)
        return jsonify({"success": True, "data": dados})

    return render_template("imoveis/visualizar.html", imovel=imovel, corretor=corretor)


@app.route("/imoveis/<int:imovel_id>", methods=["PUT"])
def atualizar_imovel(imovel_id: int):
    dados = _dados_imovel("json")
    if not dados["tipo"] or not dados["endereco"]:
        return jsonify({"success": False, "error": "Tipo e endereço são obrigatórios"}), 400
    try:
        Imovel(**dados).atualizar(imovel_id)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except KeyError:
        return jsonify({"success": False, "error": "Imóvel não encontrado"}), 404

    resposta = _serialize_record(Imovel.buscar_por_id(imovel_id))
    return jsonify({"success": True, "message": "Imóvel atualizado com sucesso", "data": resposta})


@app.route("/imoveis/<int:imovel_id>/editar", methods=["GET", "POST"])
def editar_imovel(imovel_id: int):
    imovel = Imovel.buscar_por_id(imovel_id)
    if not imovel:
        flash("❌ Imóvel não encontrado!", "error")
        return redirect(url_for("listar_imoveis"))

    if request.method == "POST":
        dados = _dados_imovel("form")
        if not dados["tipo"] or not dados["endereco"]:
            flash("❌ Tipo e endereço são obrigatórios!", "error")
            return redirect(url_for("editar_imovel", imovel_id=imovel_id))
        try:
            Imovel(**dados).atualizar(imovel_id)
        except ValueError as exc:
            flash(f"❌ {exc}", "error")
            return redirect(url_for("editar_imovel", imovel_id=imovel_id))
        flash("✏️ Imóvel atualizado com sucesso!", "success")
        return redirect(url_for("visualizar_imovel", imovel_id=imovel_id))

    return render_template(
        "imoveis/editar.html",
        imovel=imovel,
        corretores=Corretor.listar_todos(),
    )


# ---------------------------------------------------------------------------
# Interesses
# ---------------------------------------------------------------------------


def _serialize_interesse(interesse: Record) -> Dict:
    dados = _serialize_record(interesse)
    return dados


@app.route("/interesses", methods=["GET"])
def listar_interesses():
    interesses = Interesse.listar_todos()
    if wants_json():
        return jsonify({"success": True, "data": _serialize_records(interesses), "total": len(interesses)})
    return render_template("interesses/interesses.html", interesses=interesses)


@app.route("/interesses/adicionar", methods=["GET", "POST"])
def adicionar_interesse():
    if request.method == "GET":
        return render_template(
            "interesses/adicionar_interesse.html",
            clientes=Cliente.listar_todos(),
            imoveis=Imovel.listar_todos(),
        )

    origem = "json" if wants_json() else "form"
    if origem == "json":
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    cliente_id = int(data.get("cliente_id")) if data.get("cliente_id") else None
    imovel_id = int(data.get("imovel_id")) if data.get("imovel_id") else None
    status = data.get("status", "Ativo")
    observacoes = data.get("observacoes")

    if not cliente_id or not imovel_id:
        mensagem = "Cliente e imóvel são obrigatórios"
        if origem == "json":
            return jsonify({"success": False, "error": mensagem}), 400
        flash(f"❌ {mensagem}", "error")
        return redirect(url_for("adicionar_interesse"))

    try:
        Interesse(cliente_id, imovel_id, status, observacoes=observacoes).salvar()
    except ValueError as exc:
        if origem == "json":
            return jsonify({"success": False, "error": str(exc)}), 400
        flash(f"❌ {exc}", "error")
        return redirect(url_for("adicionar_interesse"))

    if origem == "json":
        interesse = Interesse.listar_todos()[-1]
        resposta = jsonify({"success": True, "data": _serialize_record(interesse)})
        resposta.status_code = 201
        return resposta

    flash("💙 Interesse registrado com sucesso!", "success")
    return redirect(url_for("listar_interesses"))


@app.route("/interesses/<int:interesse_id>", methods=["GET"])
def visualizar_interesse(interesse_id: int):
    interesse = Interesse.buscar_por_id(interesse_id)
    if not interesse:
        if wants_json():
            return jsonify({"success": False, "error": "Interesse não encontrado"}), 404
        flash("❌ Interesse não encontrado!", "error")
        return redirect(url_for("listar_interesses"))

    if wants_json():
        return jsonify({"success": True, "data": _serialize_record(interesse)})

    return render_template("interesses/visualizar_interesse.html", interesse=interesse)


@app.route("/interesses/<int:interesse_id>", methods=["DELETE"])
def remover_interesse(interesse_id: int):
    if not Interesse.deletar(interesse_id):
        return jsonify({"success": False, "error": "Interesse não encontrado"}), 404
    return jsonify({"success": True, "message": "Interesse removido"})


@app.route("/interesse/<int:interesse_id>/editar", methods=["POST"])
def atualizar_interesse(interesse_id: int):
    novo_status = request.form.get("status") or request.form.get("status_interesse")
    if not novo_status:
        flash("❌ Status é obrigatório!", "error")
        return redirect(url_for("listar_interesses"))
    Interesse.atualizar_status(interesse_id, novo_status)
    flash("Status do interesse atualizado com sucesso!", "success")
    return redirect(url_for("listar_interesses"))


@app.route("/interesse/<int:interesse_id>")
def visualizar_interesse_alias(interesse_id: int):
    return visualizar_interesse(interesse_id)


if __name__ == "__main__":
    app.run(debug=True)
