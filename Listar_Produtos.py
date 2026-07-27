import sqlite3

# Conecta ao banco
conexao = sqlite3.connect("database.db")
cursor = conexao.cursor()

# Consulta todos os produtos
cursor.execute("SELECT * FROM produtos")

# Guarda os resultados
produtos = cursor.fetchall()

# Exibe os produtos
print("=== LISTA DE PRODUTOS ===\n")

for produto in produtos:
    print(f"ID: {produto[0]}")
    print(f"Nome: {produto[1]}")
    print(f"Categoria: {produto[2]}")
    print(f"Estoque: {produto[3]}")
    print("-" * 30)

conexao.close()