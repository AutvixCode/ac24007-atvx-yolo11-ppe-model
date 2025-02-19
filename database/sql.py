import sqlite3

banco = sqlite3.connect('database/base.db')
cursor = banco.cursor()

# Excluindo tabelas anteriores, caso existam
cursor.execute("DROP TABLE IF EXISTS tripwireAlarm")
cursor.execute("DROP TABLE IF EXISTS detectModel")


# Criando a tabela 'epi'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tripwireAlarm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        hora DATETIME,
        imagem BLOB
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS detectModel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        hora DATETIME,
        a_detect BOOLEAN,
        imagem BLOB
    )
""")

banco.commit()
banco.close()
