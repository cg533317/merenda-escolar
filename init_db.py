import os
import psycopg2

def criar_tabelas():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  Variável DATABASE_URL não encontrada.")
        print("   Este script deve ser executado APÓS configurar o PostgreSQL no Render.")
        print("   Para uso local, continue usando o database.db (SQLite).")
        return

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
            cnpj TEXT
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
            quantidade NUMERIC,
            data TEXT,
            validade TEXT,
            lote TEXT,
            nota_fiscal TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saidas (
            id SERIAL PRIMARY KEY,
            produto_id INTEGER,
            escola_id INTEGER,
            quantidade NUMERIC,
            data TEXT,
            observacao TEXT
        )
    """)

    conexao.commit()
    conexao.close()
    print("✅ Tabelas criadas com sucesso no PostgreSQL!")

if __name__ == "__main__":
    criar_tabelas()
