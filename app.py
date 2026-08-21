from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import os
import sqlite3
import json
from datetime import datetime, timedelta

try:
    import psycopg2
    POSTGRES_DISPONIVEL = True
except ImportError:
    POSTGRES_DISPONIVEL = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "merenda_escolar_2026_segura")

DB = "database.db"


def conectar():
    database_url = os.environ.get('DATABASE_URL')
    if database_url and POSTGRES_DISPONIVEL:
        return psycopg2.connect(database_url)
    return sqlite3.connect(DB)


def fmt(query):
    """Adapta placeholders ? (SQLite) para %s (PostgreSQL) quando necessario"""
    if os.environ.get('DATABASE_URL') and POSTGRES_DISPONIVEL:
        return query.replace('?', '%s')
    return query


def criar_tabelas_postgres():
    """Cria as tabelas automaticamente no PostgreSQL na primeira execucao"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url or not POSTGRES_DISPONIVEL:
        return

    try:
        conexao = psycopg2.connect(database_url)
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                categoria TEXT,
                unidade TEXT,
                estoque NUMERIC DEFAULT 0,
                estoque_minimo NUMERIC DEFAULT 0,
                validade TEXT,
                lote TEXT,
                fornecedor_id INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                cnpj TEXT,
                endereco TEXT,
                contato TEXT,
                status TEXT DEFAULT 'ativo'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS escolas (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT,
                diretor TEXT,
                responsavel TEXT,
                telefone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entradas (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER,
                fornecedor_id INTEGER,
                quantidade NUMERIC,
                data TEXT,
                data_iso TEXT,
                hora TEXT,
                validade TEXT,
                lote TEXT,
                nota_fiscal TEXT,
                observacao TEXT,
                responsavel TEXT,
                deleted_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saidas (
                id SERIAL PRIMARY KEY,
                produto_id INTEGER,
                escola_id INTEGER,
                quantidade NUMERIC,
                data TEXT,
                data_iso TEXT,
                hora TEXT,
                observacao TEXT,
                responsavel TEXT,
                deleted_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id SERIAL PRIMARY KEY,
                tabela TEXT NOT NULL,
                registro_id INTEGER,
                acao TEXT NOT NULL,
                dados_anteriores TEXT,
                dados_novos TEXT,
                responsavel TEXT,
                data TEXT,
                hora TEXT,
                data_iso TEXT
            )
        """)

        conexao.commit()
        conexao.close()
        print("Tabelas criadas/verificadas no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


criar_tabelas_postgres()


# ============ BACKUP TEMPORARIO (REMOVER APOS USO) ============
@app.route("/backup")
def backup():
    senha = request.args.get("senha", "")
    if senha != "b4ckup_m3r3nd4":
        return "<h1>Acesso negado</h1>", 403

    conexao = conectar()
    cursor = conexao.cursor()
    db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') and POSTGRES_DISPONIVEL else "SQLite"

    sql_lines = []
    sql_lines.append(f"-- BACKUP SISTEMA MERENDA ESCOLAR")
    sql_lines.append(f"-- Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sql_lines.append(f"-- Banco: {db_type}")
    sql_lines.append("")

    if db_type == "PostgreSQL":
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
    else:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")

    tabelas = [t[0] for t in cursor.fetchall()]

    for tabela in tabelas:
        cursor.execute(f'SELECT * FROM "{tabela}"')
        rows = cursor.fetchall()
        if not rows:
            continue

        cursor.execute(f'PRAGMA table_info("{tabela}")') if db_type == "SQLite" else cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public' ORDER BY ordinal_position
        """, (tabela,))
        colunas = [c[1] if db_type == "SQLite" else c[0] for c in cursor.fetchall()]

        sql_lines.append(f"-- Tabela: {tabela} ({len(rows)} registros)")
        sql_lines.append(f"TRUNCATE TABLE {tabela} CASCADE;") if db_type == "PostgreSQL" else sql_lines.append(f"DELETE FROM {tabela};")

        for row in rows:
            vals = []
            for v in row:
                if v is None:
                    vals.append("NULL")
                elif isinstance(v, str):
                    vals.append("'" + str(v).replace("'", "''") + "'")
                else:
                    vals.append(str(v))
            sql_lines.append(f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({', '.join(vals)});")

        sql_lines.append("")

    conexao.close()

    sql_content = "\n".join(sql_lines)
    response = make_response(sql_content)
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = f"attachment; filename=backup_merenda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    return response


# ============ MIGRACAO TEMPORARIA (REMOVER APOS USO) ============
@app.route("/migrar")
def migrar():
    senha = request.args.get("senha", "")
    if senha != "m1gr4c40_m3r3nd4":
        return "<h1>Acesso negado</h1>", 403

    conexao = conectar()
    cursor = conexao.cursor()
    db_type = "PostgreSQL" if os.environ.get('DATABASE_URL') and POSTGRES_DISPONIVEL else "SQLite"
    logs = []

    def coluna_existe(tabela, coluna):
        try:
            if db_type == "PostgreSQL":
                cursor.execute("""
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name=%s AND column_name=%s AND table_schema='public'
                """, (tabela, coluna))
                return cursor.fetchone() is not None
            else:
                cursor.execute(f"PRAGMA table_info({tabela})")
                return any(c[1] == coluna for c in cursor.fetchall())
        except:
            return False

    # Fornecedores
    if not coluna_existe("fornecedores", "endereco"):
        cursor.execute("ALTER TABLE fornecedores ADD COLUMN endereco TEXT")
        logs.append("+ fornecedores.endereco")
    if not coluna_existe("fornecedores", "contato"):
        cursor.execute("ALTER TABLE fornecedores ADD COLUMN contato TEXT")
        logs.append("+ fornecedores.contato")
    if not coluna_existe("fornecedores", "status"):
        cursor.execute("ALTER TABLE fornecedores ADD COLUMN status TEXT DEFAULT 'ativo'")
        logs.append("+ fornecedores.status")

    # Entradas
    for col in ["fornecedor_id", "data_iso", "hora", "observacao", "responsavel", "deleted_at"]:
        if not coluna_existe("entradas", col):
            cursor.execute(f"ALTER TABLE entradas ADD COLUMN {col} TEXT")
            logs.append(f"+ entradas.{col}")

    # Saidas
    for col in ["data_iso", "hora", "responsavel", "deleted_at"]:
        if not coluna_existe("saidas", col):
            cursor.execute(f"ALTER TABLE saidas ADD COLUMN {col} TEXT")
            logs.append(f"+ saidas.{col}")

    # Preencher data_iso para registros antigos
    try:
        cursor.execute("UPDATE entradas SET data_iso = data, hora = '00:00:00', responsavel = 'Sistema' WHERE data_iso IS NULL AND data IS NOT NULL")
        logs.append("~ entradas: preenchido data_iso antigos")
    except:
        pass
    try:
        cursor.execute("UPDATE saidas SET data_iso = data, hora = '00:00:00', responsavel = 'Sistema' WHERE data_iso IS NULL AND data IS NOT NULL")
        logs.append("~ saidas: preenchido data_iso antigos")
    except:
        pass

    conexao.commit()
    conexao.close()

    return f"<h1>Migracao concluida</h1><pre>{chr(10).join(logs)}</pre><hr><p style='color:red'><b>REMOVER OS ENDPOINTS /backup E /migrar APOS USO!</b></p>"


# ============ LOGIN / LOGOUT ============
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "admin":
            session["usuario"] = usuario
            session["nome"] = "Administrador"
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario ou senha incorretos!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Voce saiu do sistema.", "info")
    return redirect(url_for("login"))


# ============ DASHBOARD ============
@app.route("/")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(estoque) FROM produtos")
    total_estoque = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM fornecedores")
    total_fornecedores = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM escolas")
    total_escolas = cursor.fetchone()[0]

    hoje = datetime.now()
    cursor.execute("SELECT nome, validade, estoque, estoque_minimo FROM produtos")
    produtos = cursor.fetchall()

    vencidos = 0
    proximos = 0
    estoque_baixo = 0

    for p in produtos:
        nome, validade, estoque, est_min = p
        if estoque <= est_min:
            estoque_baixo += 1
        if validade:
            try:
                v = datetime.strptime(validade, "%d/%m/%Y")
                if v < hoje:
                    vencidos += 1
                elif v <= hoje + timedelta(days=30):
                    proximos += 1
            except:
                pass

    conexao.close()

    return render_template("dashboard.html",
                           total_produtos=total_produtos,
                           total_estoque=total_estoque,
                           total_fornecedores=total_fornecedores,
                           total_escolas=total_escolas,
                           vencidos=vencidos,
                           proximos=proximos,
                           estoque_baixo=estoque_baixo)


# ============ PRODUTOS ============
@app.route("/produtos")
def produtos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT p.*, f.nome as fornecedor_nome
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.nome
    """)
    produtos = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM fornecedores")
    fornecedores = cursor.fetchall()

    conexao.close()
    return render_template("produtos.html", produtos=produtos, fornecedores=fornecedores)


@app.route("/produtos/cadastrar", methods=["POST"])
def cadastrar_produto():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nome = request.form["nome"]
    categoria = request.form["categoria"]
    unidade = request.form["unidade"]
    estoque = float(request.form["estoque"])
    estoque_minimo = float(request.form["estoque_minimo"])
    validade = request.form["validade"] or None
    lote = request.form["lote"] or None
    fornecedor_id = request.form["fornecedor_id"] or None

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("""
        INSERT INTO produtos (nome, categoria, unidade, estoque, estoque_minimo, validade, lote, fornecedor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """), (nome, categoria, unidade, estoque, estoque_minimo, validade, lote, fornecedor_id))
    conexao.commit()
    conexao.close()

    flash("Produto cadastrado com sucesso!", "success")
    return redirect(url_for("produtos"))


@app.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        categoria = request.form["categoria"]
        unidade = request.form["unidade"]
        estoque = float(request.form["estoque"])
        estoque_minimo = float(request.form["estoque_minimo"])
        validade = request.form["validade"] or None
        lote = request.form["lote"] or None
        fornecedor_id = request.form["fornecedor_id"] or None

        cursor.execute(fmt("""
            UPDATE produtos SET nome=?, categoria=?, unidade=?, estoque=?,
            estoque_minimo=?, validade=?, lote=?, fornecedor_id=? WHERE id=?
        """), (nome, categoria, unidade, estoque, estoque_minimo, validade, lote, fornecedor_id, id))
        conexao.commit()
        conexao.close()
        flash("Produto atualizado!", "success")
        return redirect(url_for("produtos"))

    cursor.execute(fmt("SELECT * FROM produtos WHERE id = ?"), (id,))
    produto = cursor.fetchone()

    cursor.execute("SELECT id, nome FROM fornecedores")
    fornecedores = cursor.fetchall()

    conexao.close()
    return render_template("produto_editar.html", produto=produto, fornecedores=fornecedores)


@app.route("/produtos/excluir/<int:id>")
def excluir_produto(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM produtos WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("Produto excluido!", "danger")
    return redirect(url_for("produtos"))


# ============ FORNECEDORES ============
@app.route("/fornecedores")
def fornecedores():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM fornecedores ORDER BY nome")
    fornecedores = cursor.fetchall()
    conexao.close()
    return render_template("fornecedores.html", fornecedores=fornecedores)


@app.route("/fornecedores/cadastrar", methods=["POST"])
def cadastrar_fornecedor():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nome = request.form["nome"]
    telefone = request.form["telefone"]
    email = request.form["email"]
    cnpj = request.form["cnpj"]
    endereco = request.form.get("endereco", "")
    contato = request.form.get("contato", "")
    status = request.form.get("status", "ativo")

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("""
        INSERT INTO fornecedores (nome, telefone, email, cnpj, endereco, contato, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """), (nome, telefone, email, cnpj, endereco, contato, status))
    conexao.commit()
    conexao.close()

    flash("Fornecedor cadastrado!", "success")
    return redirect(url_for("fornecedores"))


@app.route("/fornecedores/editar/<int:id>", methods=["GET", "POST"])
def editar_fornecedor(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]
        cnpj = request.form["cnpj"]
        endereco = request.form.get("endereco", "")
        contato = request.form.get("contato", "")
        status = request.form.get("status", "ativo")

        cursor.execute(fmt("""
            UPDATE fornecedores SET nome=?, telefone=?, email=?, cnpj=?,
            endereco=?, contato=?, status=? WHERE id=?
        """), (nome, telefone, email, cnpj, endereco, contato, status, id))
        conexao.commit()
        conexao.close()
        flash("Fornecedor atualizado!", "success")
        return redirect(url_for("fornecedores"))

    cursor.execute(fmt("SELECT * FROM fornecedores WHERE id = ?"), (id,))
    fornecedor = cursor.fetchone()
    conexao.close()
    return render_template("fornecedor_editar.html", fornecedor=fornecedor)


@app.route("/fornecedores/excluir/<int:id>")
def excluir_fornecedor(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM fornecedores WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("Fornecedor excluido!", "danger")
    return redirect(url_for("fornecedores"))


# ============ ESCOLAS ============
@app.route("/escolas")
def escolas():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM escolas ORDER BY nome")
    escolas = cursor.fetchall()
    conexao.close()
    return render_template("escolas.html", escolas=escolas)


@app.route("/escolas/cadastrar", methods=["POST"])
def cadastrar_escola():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nome = request.form["nome"]
    endereco = request.form["endereco"]
    diretor = request.form["diretor"]
    responsavel = request.form["responsavel"]
    telefone = request.form["telefone"]

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("""
        INSERT INTO escolas (nome, endereco, diretor, responsavel, telefone)
        VALUES (?, ?, ?, ?, ?)
    """), (nome, endereco, diretor, responsavel, telefone))
    conexao.commit()
    conexao.close()

    flash("Escola cadastrada!", "success")
    return redirect(url_for("escolas"))


@app.route("/escolas/editar/<int:id>", methods=["GET", "POST"])
def editar_escola(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        endereco = request.form["endereco"]
        diretor = request.form["diretor"]
        responsavel = request.form["responsavel"]
        telefone = request.form["telefone"]

        cursor.execute(fmt("""
            UPDATE escolas SET nome=?, endereco=?, diretor=?, responsavel=?, telefone=?
            WHERE id=?
        """), (nome, endereco, diretor, responsavel, telefone, id))
        conexao.commit()
        conexao.close()
        flash("Escola atualizada!", "success")
        return redirect(url_for("escolas"))

    cursor.execute(fmt("SELECT * FROM escolas WHERE id = ?"), (id,))
    escola = cursor.fetchone()
    conexao.close()
    return render_template("escola_editar.html", escola=escola)


@app.route("/escolas/excluir/<int:id>")
def excluir_escola(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM escolas WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("Escola excluida!", "danger")
    return redirect(url_for("escolas"))


@app.route("/escolas/<int:id>/recebimentos")
def escola_recebimentos(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    mes = request.args.get("mes", "")
    ano = request.args.get("ano", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("SELECT * FROM escolas WHERE id = ?"), (id,))
    escola = cursor.fetchone()

    query = """
        SELECT s.id, p.nome, s.quantidade, s.data, s.hora, s.observacao, s.responsavel
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        WHERE s.escola_id = ? AND s.deleted_at IS NULL
    """
    params = [id]

    if mes and ano:
        query += " AND s.data LIKE ?"
        params.append(f"%/{mes}/{ano}")
    elif data_inicio and data_fim:
        query += " AND s.data_iso >= ? AND s.data_iso <= ?"
        params.extend([data_inicio, data_fim])

    query += " ORDER BY s.data_iso DESC, s.hora DESC"

    cursor.execute(fmt(query), tuple(params))
    recebimentos = cursor.fetchall()

    cursor.execute(fmt("""
        SELECT p.nome, SUM(s.quantidade) as total
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        WHERE s.escola_id = ? AND s.deleted_at IS NULL
        GROUP BY p.nome
        ORDER BY total DESC
    """), (id,))
    resumo = cursor.fetchall()

    conexao.close()
    return render_template("escola_recebimentos.html",
                           escola=escola,
                           recebimentos=recebimentos,
                           resumo=resumo,
                           mes=mes, ano=ano,
                           data_inicio=data_inicio, data_fim=data_fim)


# ============ MOVIMENTACAO ============
@app.route("/movimentacao")
def movimentacao():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
    escolas = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM fornecedores ORDER BY nome")
    fornecedores = cursor.fetchall()

    conexao.close()
    return render_template("movimentacao.html", produtos=produtos, escolas=escolas, fornecedores=fornecedores)


@app.route("/movimentacao/entrada", methods=["POST"])
def registrar_entrada():
    if "usuario" not in session:
        return redirect(url_for("login"))

    produto_id = int(request.form["produto_id"])
    fornecedor_id = request.form.get("fornecedor_id") or None
    quantidade = float(request.form["quantidade"])
    nota_fiscal = request.form["nota_fiscal"] or None
    lote = request.form["lote"] or None
    validade = request.form["validade"] or None
    observacao = request.form.get("observacao", "")
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    data_iso = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    responsavel = session.get("nome", "Administrador")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("""
        INSERT INTO entradas (produto_id, fornecedor_id, quantidade, data, data_iso, hora,
                              validade, lote, nota_fiscal, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """), (produto_id, fornecedor_id, quantidade, data_hoje, data_iso, hora,
            validade, lote, nota_fiscal, observacao, responsavel))

    cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
    estoque_atual = cursor.fetchone()[0]
    novo_estoque = estoque_atual + quantidade
    cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

    conexao.commit()
    conexao.close()

    flash(f"Entrada de {quantidade} unidades registrada!", "success")
    return redirect(url_for("movimentacao"))


@app.route("/movimentacao/saida", methods=["POST"])
def registrar_saida():
    if "usuario" not in session:
        return redirect(url_for("login"))

    produto_id = int(request.form["produto_id"])
    escola_id = request.form["escola_id"] or None
    quantidade = float(request.form["quantidade"])
    observacao = request.form["observacao"] or None
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    data_iso = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    responsavel = session.get("nome", "Administrador")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
    estoque_atual = cursor.fetchone()[0]

    if quantidade > estoque_atual:
        conexao.close()
        flash("Estoque insuficiente!", "danger")
        return redirect(url_for("movimentacao"))

    cursor.execute(fmt("""
        INSERT INTO saidas (produto_id, escola_id, quantidade, data, data_iso, hora, observacao, responsavel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """), (produto_id, escola_id, quantidade, data_hoje, data_iso, hora, observacao, responsavel))

    novo_estoque = estoque_atual - quantidade
    cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

    conexao.commit()
    conexao.close()

    flash(f"Saida de {quantidade} unidades registrada!", "success")
    return redirect(url_for("movimentacao"))


# ============ SAIDAS (MODULO EXCLUSIVO) ============
@app.route("/saidas")
def saidas():
    if "usuario" not in session:
        return redirect(url_for("login"))

    escola_id = request.args.get("escola_id", "")
    produto_id = request.args.get("produto_id", "")
    mes = request.args.get("mes", "")
    ano = request.args.get("ano", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    conexao = conectar()
    cursor = conexao.cursor()

    query = """
        SELECT s.id, p.nome, s.quantidade, s.data, s.hora, e.nome as escola_nome,
               s.observacao, s.responsavel
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        LEFT JOIN escolas e ON s.escola_id = e.id
        WHERE s.deleted_at IS NULL
    """
    params = []

    if escola_id:
        query += " AND s.escola_id = ?"
        params.append(escola_id)
    if produto_id:
        query += " AND s.produto_id = ?"
        params.append(produto_id)
    if mes and ano:
        query += " AND s.data LIKE ?"
        params.append(f"%/{mes}/{ano}")
    elif data_inicio and data_fim:
        query += " AND s.data_iso >= ? AND s.data_iso <= ?"
        params.extend([data_inicio, data_fim])

    query += " ORDER BY s.data_iso DESC, s.hora DESC"

    cursor.execute(fmt(query), tuple(params))
    saidas = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
    escolas = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()

    conexao.close()
    return render_template("saidas.html", saidas=saidas, escolas=escolas, produtos=produtos,
                           escola_id=escola_id, produto_id=produto_id,
                           mes=mes, ano=ano, data_inicio=data_inicio, data_fim=data_fim)


@app.route("/saidas/estornar/<int:id>", methods=["POST"])
def estornar_saida(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("SELECT produto_id, quantidade FROM saidas WHERE id = ?"), (id,))
    registro = cursor.fetchone()

    if registro:
        produto_id, quantidade = registro
        cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
        estoque_atual = cursor.fetchone()[0]
        novo_estoque = estoque_atual + quantidade
        cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

        data_hoje = datetime.now().strftime("%d/%m/%Y")
        cursor.execute(fmt("UPDATE saidas SET deleted_at = ? WHERE id = ?"), (data_hoje, id))
        conexao.commit()
        flash("Saida estornada! Estoque restaurado.", "warning")

    conexao.close()
    return redirect(url_for("saidas"))


# ============ ENTRADAS (MODULO EXCLUSIVO) ============
@app.route("/entradas")
def entradas():
    if "usuario" not in session:
        return redirect(url_for("login"))

    fornecedor_id = request.args.get("fornecedor_id", "")
    produto_id = request.args.get("produto_id", "")
    mes = request.args.get("mes", "")
    ano = request.args.get("ano", "")
    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    conexao = conectar()
    cursor = conexao.cursor()

    query = """
        SELECT e.id, p.nome, e.quantidade, e.data, e.hora, f.nome as fornecedor_nome,
               e.nota_fiscal, e.observacao, e.responsavel
        FROM entradas e
        JOIN produtos p ON e.produto_id = p.id
        LEFT JOIN fornecedores f ON e.fornecedor_id = f.id
        WHERE e.deleted_at IS NULL
    """
    params = []

    if fornecedor_id:
        query += " AND e.fornecedor_id = ?"
        params.append(fornecedor_id)
    if produto_id:
        query += " AND e.produto_id = ?"
        params.append(produto_id)
    if mes and ano:
        query += " AND e.data LIKE ?"
        params.append(f"%/{mes}/{ano}")
    elif data_inicio and data_fim:
        query += " AND e.data_iso >= ? AND e.data_iso <= ?"
        params.extend([data_inicio, data_fim])

    query += " ORDER BY e.data_iso DESC, e.hora DESC"

    cursor.execute(fmt(query), tuple(params))
    entradas = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM fornecedores ORDER BY nome")
    fornecedores = cursor.fetchall()

    cursor.execute("SELECT id, nome FROM produtos ORDER BY nome")
    produtos = cursor.fetchall()

    conexao.close()
    return render_template("entradas.html", entradas=entradas, fornecedores=fornecedores, produtos=produtos,
                           fornecedor_id=fornecedor_id, produto_id=produto_id,
                           mes=mes, ano=ano, data_inicio=data_inicio, data_fim=data_fim)


@app.route("/entradas/estornar/<int:id>", methods=["POST"])
def estornar_entrada(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("SELECT produto_id, quantidade FROM entradas WHERE id = ?"), (id,))
    registro = cursor.fetchone()

    if registro:
        produto_id, quantidade = registro
        cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
        estoque_atual = cursor.fetchone()[0]
        novo_estoque = estoque_atual - quantidade
        if novo_estoque < 0:
            novo_estoque = 0
        cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

        data_hoje = datetime.now().strftime("%d/%m/%Y")
        cursor.execute(fmt("UPDATE entradas SET deleted_at = ? WHERE id = ?"), (data_hoje, id))
        conexao.commit()
        flash("Entrada estornada! Estoque ajustado.", "warning")

    conexao.close()
    return redirect(url_for("entradas"))


# ============ RELATORIOS ============
@app.route("/sobre")
def sobre():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("sobre.html")


@app.route("/relatorios")
def relatorios():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT p.nome, p.categoria, p.estoque, p.estoque_minimo, p.validade, f.nome
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.nome
    """)
    produtos = cursor.fetchall()

    cursor.execute("""
        SELECT e.id, p.nome, e.quantidade, e.data, e.nota_fiscal
        FROM entradas e
        JOIN produtos p ON e.produto_id = p.id
        WHERE e.deleted_at IS NULL
        ORDER BY e.data DESC LIMIT 20
    """)
    entradas = cursor.fetchall()

    cursor.execute("""
        SELECT s.id, p.nome, s.quantidade, s.data, e.nome
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        LEFT JOIN escolas e ON s.escola_id = e.id
        WHERE s.deleted_at IS NULL
        ORDER BY s.data DESC LIMIT 20
    """)
    saidas = cursor.fetchall()

    conexao.close()
    return render_template("relatorios.html", produtos=produtos, entradas=entradas, saidas=saidas)


# ============ PDF / IMPRESSAO ============
@app.route("/relatorios/imprimir")
def relatorio_imprimir():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        SELECT p.nome, p.categoria, p.estoque, p.estoque_minimo, p.unidade, p.validade, f.nome
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.categoria, p.nome
    """)
    produtos = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, e.quantidade, e.data, e.nota_fiscal
        FROM entradas e
        JOIN produtos p ON e.produto_id = p.id
        WHERE e.deleted_at IS NULL
        ORDER BY e.data DESC
    """)
    entradas = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, s.quantidade, s.data, e.nome as escola
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        LEFT JOIN escolas e ON s.escola_id = e.id
        WHERE s.deleted_at IS NULL
        ORDER BY s.data DESC
    """)
    saidas = cursor.fetchall()

    conexao.close()

    return render_template("relatorio_imprimir.html",
                           produtos=produtos,
                           entradas=entradas,
                           saidas=saidas,
                           data_atual=hoje)


@app.route("/relatorios/pdf")
def relatorio_pdf():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        from weasyprint import HTML, CSS

        conexao = conectar()
        cursor = conexao.cursor()
        hoje = datetime.now().strftime("%d/%m/%Y")

        cursor.execute("""
            SELECT p.nome, p.categoria, p.estoque, p.estoque_minimo, p.unidade, p.validade, f.nome
            FROM produtos p
            LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
            ORDER BY p.categoria, p.nome
        """)
        produtos = cursor.fetchall()

        cursor.execute("""
            SELECT p.nome, e.quantidade, e.data, e.nota_fiscal
            FROM entradas e
            JOIN produtos p ON e.produto_id = p.id
            WHERE e.deleted_at IS NULL
            ORDER BY e.data DESC
        """)
        entradas = cursor.fetchall()

        cursor.execute("""
            SELECT p.nome, s.quantidade, s.data, e.nome as escola
            FROM saidas s
            JOIN produtos p ON s.produto_id = p.id
            LEFT JOIN escolas e ON s.escola_id = e.id
            WHERE s.deleted_at IS NULL
            ORDER BY s.data DESC
        """)
        saidas = cursor.fetchall()
        conexao.close()

        html = render_template("relatorio_pdf.html",
                               produtos=produtos,
                               entradas=entradas,
                               saidas=saidas,
                               data_atual=hoje)

        pdf = HTML(string=html).write_pdf()

        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=relatorio_merenda.pdf"
        return response

    except ImportError:
        flash("Biblioteca weasyprint nao instalada. Use o botao Imprimir do navegador!", "warning")
        return redirect(url_for("relatorios"))
    except Exception as e:
        flash(f"Erro ao gerar PDF: {str(e)}", "danger")
        return redirect(url_for("relatorios"))


if __name__ == "__main__":
    app.run(debug=True)
