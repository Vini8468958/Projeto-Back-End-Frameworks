import requests

# IMPORTANTE: Esta URL deve ser atualizada sempre que o servidor for reiniciado.
BASE_URL = "https://8a36e5500b80.ngrok-free.app"

# ##########################################################################
# ## SOLUÇÃO: Este cabeçalho especial ignora a página de aviso do ngrok. ##
# ##########################################################################
HEADERS = {"ngrok-skip-browser-warning": "true"}

def listar_tarefas():
    """Faz a requisição GET para buscar todas as tarefas."""
    try:
        # Adicionamos o 'headers=HEADERS' a todas as requisições
        response = requests.get(f"{BASE_URL}/tasks", headers=HEADERS)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\nErro de conexão ao listar tarefas: {e}")
        return None

def criar_tarefa(titulo, descricao):
    """Faz a requisição POST para criar uma nova tarefa."""
    nova_tarefa = {"titulo": titulo, "descricao": descricao}
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=nova_tarefa, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"\nErro de conexão ao criar tarefa: {e}")
        return None

def deletar_tarefa(task_id):
    """Faz a requisição DELETE para remover uma tarefa."""
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"\nErro de conexão ao deletar tarefa: {e}")
        return None

