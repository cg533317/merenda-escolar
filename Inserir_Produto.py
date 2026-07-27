import sqlite3

conexao = sqlite3.connect("database.db")
cursor = conexao.cursor()

cursor.execute("""
INSERT INTO produtos (nome, categoria, estoque)
VALUES (?, ?, ?)
""", ("Arroz", "Alimentos", 50))

conexao.commit()
conexao.close()

print("Produto cadastrado com sucesso!")