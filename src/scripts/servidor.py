import http.server
import socketserver
import json
import re
from pyngrok import ngrok

# --- Configurações ---
PORT = 8000
# #############################################################################
# ## IMPORTANTE: Insira o seu token de autenticação do Ngrok aqui          ##
# #############################################################################
NGROK_AUTH_TOKEN = "32Bvo2Y2fKQ9lv3NnEs9RdEpnJZ_3Z8bZissoyT71en9D5XFa"

# --- Banco de Dados Simulado (Começa Vazio) ---
TAREFAS_MOCK = []
ultimo_id = 0

class TaskHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # DEBUG: Imprime a requisição recebida no terminal do servidor
        print(f"[SERVIDOR] Recebida requisição GET para o caminho: '{self.path}'")

        # Rota para buscar uma tarefa específica: /tasks/1
        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            tarefa = next((t for t in TAREFAS_MOCK if t['id'] == task_id), None)
            if tarefa:
                self._send_response(200, tarefa)
            else:
                self._send_error_response(404, "Tarefa não encontrada.")
        # Rota para listar todas as tarefas
        elif self.path == '/tasks':
            self._send_response(200, TAREFAS_MOCK)
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    def do_POST(self):
        # DEBUG: Imprime a requisição recebida no terminal do servidor
        print(f"[SERVIDOR] Recebida requisição POST para o caminho: '{self.path}'")
        
        global ultimo_id
        if self.path == '/tasks':
            try:
                dados = self._get_json_body()
                if 'titulo' not in dados:
                    self._send_error_response(400, "O campo 'titulo' é obrigatório.")
                    return

                ultimo_id += 1
                nova_tarefa = {
                    "id": ultimo_id,
                    "titulo": dados['titulo'],
                    "descricao": dados.get('descricao', ''),
                    "status": "pendente"
                }
                TAREFAS_MOCK.append(nova_tarefa)
                self._send_response(201, nova_tarefa)
            except (json.JSONDecodeError, ValueError):
                self._send_error_response(400, "Corpo da requisição inválido.")
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    def do_DELETE(self):
        # DEBUG: Imprime a requisição recebida no terminal do servidor
        print(f"[SERVIDOR] Recebida requisição DELETE para o caminho: '{self.path}'")

        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            tarefa = next((t for t in TAREFAS_MOCK if t['id'] == task_id), None)

            if tarefa:
                TAREFAS_MOCK.remove(tarefa)
                self.send_response(204)
                self.end_headers()
            else:
                self._send_error_response(404, "Tarefa não encontrada.")
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")

    def do_PUT(self):
        print(f"[SERVIDOR] Recebida requisição PUT para o caminho: '{self.path}'")

        match = re.match(r'/tasks/(\d+)', self.path)
        if match:
            task_id = int(match.group(1))
            tarefa = next((t for t in TAREFAS_MOCK if t['id'] == task_id), None)

            if tarefa:
                try:
                    dados = self._get_json_body()
                    if 'titulo' in dados:
                        tarefa['titulo'] = dados['titulo']
                    if 'descricao' in dados:
                        tarefa['descricao'] = dados['descricao']
                    if 'status' in dados:
                        tarefa['status'] = dados['status']

                    self._send_response(200, tarefa)
                except (json.JSONDecodeError, ValueError):
                    self._send_error_response(400, "Corpo da requisição inválido.")
            else:
                self._send_error_response(404, "Tarefa não encontrada.")
        else:
            self._send_error_response(404, "Caminho não encontrado no servidor.")        

    # --- Funções Auxiliares ---
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

# --- Bloco Principal para Iniciar o Servidor e o Túnel Ngrok ---
if __name__ == "__main__":
    if NGROK_AUTH_TOKEN == "SEU_TOKEN_AQUI":
        print("!!! ERRO: Por favor, configure o seu NGROK_AUTH_TOKEN !!!")
    else:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        with socketserver.TCPServer(("", PORT), TaskHandler) as httpd:
            public_url = ngrok.connect(PORT, "http")
            print("==================================================")
            print(f"Servidor local a rodar em: http://localhost:{PORT}")
            print(f"URL pública do Ngrok: {public_url}")
            print("==================================================")
            try:
                httpd.serve_forever()
            finally:
                ngrok.disconnect(public_url)
                print("\nTúnel do Ngrok fechado.")
