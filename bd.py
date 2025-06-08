import sqlite3

ceps = [
    ("01001000", "Praça da Sé", "lado ímpar", "Sé", "São Paulo", "SP", "3550308", "11"),
    ("20040002", "Rua da Assembleia", "", "Centro", "Rio de Janeiro", "RJ", "3304557", "21"),
    ("30140071", "Avenida do Contorno", "até 1277", "Floresta", "Belo Horizonte", "MG", "3106200", "31"),
    ("70040900", "Esplanada dos Ministérios", "Bloco X", "Zona Cívico-Administrativa", "Brasília", "DF", "5300108", "61"),
    ("88010001", "Rua Felipe Schmidt", "", "Centro", "Florianópolis", "SC", "4205407", "48")
]

conn = sqlite3.connect('ceps.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS ceps (
    cep TEXT PRIMARY KEY,
    logradouro TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf TEXT,
    ibge TEXT,
    ddd TEXT
)
''')

cursor.executemany('''
INSERT OR REPLACE INTO ceps VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ceps)

conn.commit()
conn.close()
