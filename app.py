from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import os
import sqlite3
from datetime import datetime, timedelta

try:
    import psycopg2
    POSTGRES_DISPONIVEL = True
except ImportError:
    POSTGRES_DISPONIVEL = False

app = Flask(__name__)
app.secret_key = "merenda_escolar_2026_segura"

DB = "database.db"

def conectar():
    database_url = os.environ.get('DATABASE_URL')
    if database_url and POSTGRES_DISPONIVEL:
        return psycopg2.connect(database_url)
    return sqlite3.connect(DB)

def fmt(query):
    """Adapta placeholders ? (SQLite) para %s (PostgreSQL) quando necessário"""
    if os.environ.get('DATABASE_URL') and POSTGRES_DISPONIVEL:
        return query.replace('?', '%s')
    return query


# ============ LOGIN / LOGOUT ============

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "admin" and senha == "admin":
            session["usuario"] = usuario
            session["nome"] = "Administrador"
            flash("✅ Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Usuário ou senha incorretos!", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("👋 Você saiu do sistema.", "info")
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

    flash("✅ Produto cadastrado com sucesso!", "success")
    return redirect(url_for("produtos"))


@app.route("/produtos/excluir/<int:id>")
def excluir_produto(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM produtos WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("🗑️ Produto excluído!", "danger")
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

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("""
        INSERT INTO fornecedores (nome, telefone, email, cnpj)
        VALUES (?, ?, ?, ?)
    """), (nome, telefone, email, cnpj))
    conexao.commit()
    conexao.close()

    flash("✅ Fornecedor cadastrado!", "success")
    return redirect(url_for("fornecedores"))


@app.route("/fornecedores/excluir/<int:id>")
def excluir_fornecedor(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM fornecedores WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("🗑️ Fornecedor excluído!", "danger")
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

    flash("✅ Escola cadastrada!", "success")
    return redirect(url_for("escolas"))


@app.route("/escolas/excluir/<int:id>")
def excluir_escola(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(fmt("DELETE FROM escolas WHERE id = ?"), (id,))
    conexao.commit()
    conexao.close()
    flash("🗑️ Escola excluída!", "danger")
    return redirect(url_for("escolas"))


# ============ MOVIMENTAÇÃO ============

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

    conexao.close()
    return render_template("movimentacao.html", produtos=produtos, escolas=escolas)


@app.route("/movimentacao/entrada", methods=["POST"])
def registrar_entrada():
    if "usuario" not in session:
        return redirect(url_for("login"))

    produto_id = int(request.form["produto_id"])
    quantidade = float(request.form["quantidade"])
    nota_fiscal = request.form["nota_fiscal"] or None
    lote = request.form["lote"] or None
    validade = request.form["validade"] or None
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("""
        INSERT INTO entradas (produto_id, quantidade, data, validade, lote, nota_fiscal)
        VALUES (?, ?, ?, ?, ?, ?)
    """), (produto_id, quantidade, data_hoje, validade, lote, nota_fiscal))

    cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
    estoque_atual = cursor.fetchone()[0]
    novo_estoque = estoque_atual + quantidade
    cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

    conexao.commit()
    conexao.close()

    flash(f"✅ Entrada de {quantidade} unidades registrada!", "success")
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

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(fmt("SELECT estoque FROM produtos WHERE id = ?"), (produto_id,))
    estoque_atual = cursor.fetchone()[0]

    if quantidade > estoque_atual:
        conexao.close()
        flash("❌ Estoque insuficiente!", "danger")
        return redirect(url_for("movimentacao"))

    cursor.execute(fmt("""
        INSERT INTO saidas (produto_id, escola_id, quantidade, data, observacao)
        VALUES (?, ?, ?, ?, ?)
    """), (produto_id, escola_id, quantidade, data_hoje, observacao))

    novo_estoque = estoque_atual - quantidade
    cursor.execute(fmt("UPDATE produtos SET estoque = ? WHERE id = ?"), (novo_estoque, produto_id))

    conexao.commit()
    conexao.close()

    flash(f"✅ Saída de {quantidade} unidades registrada!", "success")
    return redirect(url_for("movimentacao"))


# ============ RELATÓRIOS ============

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
        SELECT p.nome, p.estoque, p.estoque_minimo, p.unidade, p.validade, f.nome
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.nome
    """)
    produtos = cursor.fetchall()

    cursor.execute("""
        SELECT e.id, p.nome, e.quantidade, e.data, e.nota_fiscal
        FROM entradas e
        JOIN produtos p ON e.produto_id = p.id
        ORDER BY e.data DESC LIMIT 20
    """)
    entradas = cursor.fetchall()

    cursor.execute("""
        SELECT s.id, p.nome, s.quantidade, s.data, e.nome
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        LEFT JOIN escolas e ON s.escola_id = e.id
        ORDER BY s.data DESC LIMIT 20
    """)
    saidas = cursor.fetchall()

    conexao.close()
    return render_template("relatorios.html", produtos=produtos, entradas=entradas, saidas=saidas)


# ============ PDF / IMPRESSÃO ============

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
        ORDER BY e.data DESC
    """)
    entradas = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, s.quantidade, s.data, e.nome as escola
        FROM saidas s
        JOIN produtos p ON s.produto_id = p.id
        LEFT JOIN escolas e ON s.escola_id = e.id
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
        import tempfile

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
            ORDER BY e.data DESC
        """)
        entradas = cursor.fetchall()

        cursor.execute("""
            SELECT p.nome, s.quantidade, s.data, e.nome as escola
            FROM saidas s
            JOIN produtos p ON s.produto_id = p.id
            LEFT JOIN escolas e ON s.escola_id = e.id
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
        flash("⚠️ Biblioteca weasyprint não instalada. Use o botão Imprimir do navegador!", "warning")
        return redirect(url_for("relatorios"))
    except Exception as e:
        flash(f"❌ Erro ao gerar PDF: {str(e)}", "danger")
        return redirect(url_for("relatorios"))


if __name__ == "__main__":
    app.run(debug=True)
