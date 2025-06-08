from flask import Flask, jsonify, abort
from datetime import datetime
import sqlite3
import time

app = Flask(__name__)

def consultar_cep_banco(cep):
    conn = sqlite3.connect("ceps.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ceps WHERE cep = ?", (cep,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

@app.route("/cep/<cep>")
def consultar_cep(cep):
    dados = consultar_cep_banco(cep)
    if not dados:
        abort(404, description="CEP não encontrado")
    time.sleep(0.1 + 0.3 * hash(cep) % 1)
    resposta = {
        "cep": cep,
        **dados,
        "timestamp_consulta": datetime.now().isoformat()
    }
    return jsonify(resposta)

if __name__ == "__main__":
    app.run(port=8000)
