import sqlite3

banco = sqlite3.connect('base.db')
cursor = banco.cursor()

# Excluindo tabelas anteriores, caso existam
cursor.execute("DROP TABLE IF EXISTS epi")
cursor.execute("DROP TABLE IF EXISTS area")

# Criando a tabela 'epi'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS epi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        hora DATETIME,
        imagem BLOB,
    )
""")

banco.commit()
banco.close()