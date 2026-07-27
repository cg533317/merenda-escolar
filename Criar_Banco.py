import sqlite3
conexao = sqlite3.connect("database.db")
cursor = conexao.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS produtos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT NOT NULL,
categoria TEXT,
estoque REAL DEFAULT 0

)
""")

conexao.commit()
conexao.close()

print("Banco criado com sucesso!")
