import sqlite3

conexao = sqlite3.connect("database.db")
cursor = conexao.cursor()

# Tabela de produtos (ATUALIZADA com mais campos)
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT,
    unidade TEXT DEFAULT 'kg',
    estoque REAL DEFAULT 0,
    estoque_minimo REAL DEFAULT 0,
    validade TEXT,
    lote TEXT,
    fornecedor_id INTEGER,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
)
""")

# Tabela de fornecedores
cursor.execute("""
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    cnpj TEXT
)
""")

# Tabela de escolas
cursor.execute("""
CREATE TABLE IF NOT EXISTS escolas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT,
    diretor TEXT,
    responsavel TEXT,
    telefone TEXT
)
""")

# Tabela de entradas (histórico de compras/recebimentos)
cursor.execute("""
CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    fornecedor_id INTEGER,
    quantidade REAL NOT NULL,
    data TEXT NOT NULL,
    validade TEXT,
    lote TEXT,
    nota_fiscal TEXT,
    observacao TEXT,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
)
""")

# Tabela de saídas (histórico de distribuição para escolas)
cursor.execute("""
CREATE TABLE IF NOT EXISTS saidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    escola_id INTEGER NOT NULL,
    quantidade REAL NOT NULL,
    data TEXT NOT NULL,
    observacao TEXT,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (escola_id) REFERENCES escolas(id)
)
""")

conexao.commit()
conexao.close()

print("✅ Banco de dados completo criado com sucesso!")
print("Tabelas criadas: produtos, fornecedores, escolas, entradas, saidas")