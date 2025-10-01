import http.server
import socketserver
import json
import re
import os
import sqlite3
from datetime import datetime
from pyngrok import ngrok

PORT = 8000

NGROK_AUTH_TOKEN = "32Bvo2Y2fKQ9lv3NnEs9RdEpnJZ_3Z8bZissoyT71en9D5XFa" 


DB_PATH = os.path.join("src", "data", "tarefas.db")

def conectar_bd():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  
        return conn
    except sqlite3.Error as e:
        print(f"[ERRO BD] Não foi possível conectar ao banco de dados: {e}")
        return None

def _formatar_tarefa(row):
    if not row:
        return None
    
    tarefa_dict = dict(row)
    
    
    try:
        dt_object = datetime.strptime(tarefa_dict['criado_em'], '%Y-%m-%d %H:%M:%S')
        tarefa_dict['criado_em'] = dt_object.timestamp()
    except (ValueError, TypeError):
        
        tarefa_dict['criado_em'] = None 

    return tarefa_dict


class TaskHandler(http.server.BaseHTTPRequestHandler):
    
    # --- MÉTODOS HTTP ---

    def do_GET(self):
        conn = conectar_bd()
        if not conn:
            self._send_error_response(500, "Erro interno no servidor: não foi possível conectar ao banco de dados.")
            return

        cursor = conn.cursor()
        
        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            cursor.execute("SELECT * FROM tarefas WHERE id = ?", (task_id,))
            tarefa_row = cursor.fetchone()
            
            if tarefa_row:
                self._send_response(200, _formatar_tarefa(tarefa_row))
            else:
                self._send_error_response(404, "Tarefa não encontrada.")
        elif self.path == '/tasks':
            cursor.execute("SELECT * FROM tarefas ORDER BY criado_em DESC")
            tarefas_rows = cursor.fetchall()
            tarefas_list = [_formatar_tarefa(row) for row in tarefas_rows]
            self._send_response(200, tarefas_list)
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")
        
        conn.close()

    def do_POST(self):
        if self.path == '/tasks':
            try:
                dados = self._get_json_body()
                if not dados.get('titulo') or not dados['titulo'].strip():
                    self._send_error_response(400, "O campo 'titulo' é obrigatório e não pode ser vazio.")
                    return

                conn = conectar_bd()
                if not conn:
                    self._send_error_response(500, "Erro interno no servidor.")
                    return
                
                cursor = conn.cursor()
                sql = "INSERT INTO tarefas (titulo, descricao) VALUES (?, ?)"
                cursor.execute(sql, (dados['titulo'], dados.get('descricao')))
                conn.commit()
                
                novo_id = cursor.lastrowid
                
                cursor.execute("SELECT * FROM tarefas WHERE id = ?", (novo_id,))
                nova_tarefa_row = cursor.fetchone()
                
                self._send_response(201, _formatar_tarefa(nova_tarefa_row))
                conn.close()

            except (json.JSONDecodeError, ValueError):
                self._send_error_response(400, "Corpo da requisição inválido.")
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    def do_PUT(self):
        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            conn = conectar_bd()
            if not conn:
                self._send_error_response(500, "Erro interno no servidor.")
                return

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tarefas WHERE id = ?", (task_id,))
            if not cursor.fetchone():
                self._send_error_response(404, "Tarefa não encontrada.")
                conn.close()
                return

            try:
                dados = self._get_json_body()
                sql = "UPDATE tarefas SET titulo = ?, descricao = ?, status = ? WHERE id = ?"
                cursor.execute(sql, (
                    dados.get('titulo'),
                    dados.get('descricao'),
                    dados.get('status'),
                    task_id
                ))
                conn.commit()
                
                cursor.execute("SELECT * FROM tarefas WHERE id = ?", (task_id,))
                tarefa_atualizada_row = cursor.fetchone()

                self._send_response(200, _formatar_tarefa(tarefa_atualizada_row))

            except (json.JSONDecodeError, ValueError):
                self._send_error_response(400, "Corpo da requisição inválido.")
            finally:
                conn.close()
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    def do_DELETE(self):
        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            conn = conectar_bd()
            if not conn:
                self._send_error_response(500, "Erro interno no servidor.")
                return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas WHERE id = ?", (task_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                self.send_response(204) # No Content
                self.end_headers()
            else:
                self._send_error_response(404, "Tarefa não encontrada.")
            conn.close()
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    
    def _get_json_body(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))

    def _send_response(self, status_code, body):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def _send_error_response(self, status_code, message):
        self._send_response(status_code, {"erro": message})

if __name__ == "__main__":
    if NGROK_AUTH_TOKEN != "32Bvo2Y2fKQ9lv3NnEs9RdEpnJZ_3Z8bZissoyT71en9D5XFa":
        print("ERRO: Por favor, configure o seu NGROK_AUTH_TOKEN")
    else:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        with socketserver.TCPServer(("", PORT), TaskHandler) as httpd:
            public_url = ngrok.connect(PORT, "http")
            print("==================================================")
            print(f"Servidor local rodando em: http://localhost:{PORT}")
            print(f"URL pública do Ngrok: {public_url}")
            print("==================================================")
            print("Pressione CTRL+C para parar o servidor.")
            try:
                httpd.serve_forever()
            finally:
                ngrok.disconnect(public_url)
                print("\nTúnel do Ngrok fechado.")
