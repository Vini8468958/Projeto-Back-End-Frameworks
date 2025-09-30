from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
import os

# Caminho do banco (relativo à raiz do projeto)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "tarefas.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/tasks":
            self.listar_tarefas()
        elif self.path.startswith("/tasks/"):
            task_id = self.path.split("/")[-1]
            self.buscar_tarefa(task_id)
        else:
            self.responder(404, {"erro": "Rota não encontrada"})

    def do_POST(self):
        if self.path == "/tasks":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                titulo = data.get("titulo")
                descricao = data.get("descricao", "")
                status = data.get("status", "pendente")

                if not titulo:
                    self.responder(400, {"erro": "O campo 'titulo' é obrigatório"})
                    return

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tarefas (titulo, descricao, status) VALUES (?, ?, ?)",
                    (titulo, descricao, status),
                )
                conn.commit()
                task_id = cursor.lastrowid
                conn.close()

                self.responder(201, {
                    "mensagem": "Tarefa criada com sucesso",
                    "id": task_id
                })

            except json.JSONDecodeError:
                self.responder(400, {"erro": "JSON inválido"})
        else:
            self.responder(404, {"erro": "Rota não encontrada"})

    # Auxiliares
    def listar_tarefas(self):
        conn = get_db_connection()
        tarefas = conn.execute("SELECT * FROM tarefas").fetchall()
        conn.close()
        self.responder(200, [dict(tarefa) for tarefa in tarefas])

    def buscar_tarefa(self, task_id):
        conn = get_db_connection()
        tarefa = conn.execute("SELECT * FROM tarefas WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if tarefa:
            self.responder(200, dict(tarefa))
        else:
            self.responder(404, {"erro": "Tarefa não encontrada"})

    def responder(self, status, data):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
