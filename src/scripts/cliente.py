import requests
import sys

BASE_URL = "http://localhost:8000/tasks"

def listar_tarefas():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        tarefas = response.json()
        if tarefas:
            for tarefa in tarefas:
                print(f"Tarefa {tarefa['id']}: {tarefa['titulo']} - Status: {tarefa['status']}")
        else:
            print("Nenhuma tarefa encontrada.")
    else:
        print("Erro ao listar tarefas:", response.json().get("erro", "Desconhecido"))

def visualizar_tarefa(task_id):
    response = requests.get(f"{BASE_URL}/{task_id}")
    if response.status_code == 200:
        tarefa = response.json()
        print(f"Tarefa {tarefa['id']}: {tarefa['titulo']}\nDescrição: {tarefa['descricao']}\nStatus: {tarefa['status']}")
    else:
        print("Erro ao visualizar tarefa:", response.json().get("erro", "Desconhecido"))

def criar_tarefa(titulo, descricao=""):
    dados = {"titulo": titulo, "descricao": descricao, "status": "pendente"}
    response = requests.post(BASE_URL, json=dados)
    if response.status_code == 201:
        print("Tarefa criada com sucesso! ID:", response.json()["id"])
    else:
        print("Erro ao criar tarefa:", response.json().get("erro", "Desconhecido"))

def atualizar_tarefa(task_id, status):
    dados = {"status": status}
    response = requests.put(f"{BASE_URL}/{task_id}", json=dados)
    if response.status_code == 200:
        print(f"Tarefa {task_id} atualizada para {status}")
    else:
        print("Erro ao atualizar tarefa:", response.json().get("erro", "Desconhecido"))

def deletar_tarefa(task_id):
    response = requests.delete(f"{BASE_URL}/{task_id}")
    if response.status_code == 200:
        print(f"Tarefa {task_id} deletada com sucesso.")
    else:
        print("Erro ao deletar tarefa:", response.json().get("erro", "Desconhecido"))

def main():
    if len(sys.argv) < 2:
        print("Comando necessário: criar, listar, visualizar, atualizar, deletar.")
        sys.exit(1)

    comando = sys.argv[1]

    if comando == "listar":
        listar_tarefas()
    elif comando == "visualizar" and len(sys.argv) == 3:
        visualizar_tarefa(sys.argv[2])
    elif comando == "criar" and len(sys.argv) >= 3:
        titulo = sys.argv[2]
        descricao = sys.argv[3] if len(sys.argv) > 3 else ""
        criar_tarefa(titulo, descricao)
    elif comando == "atualizar" and len(sys.argv) == 4:
        task_id = sys.argv[2]
        status = sys.argv[3]
        atualizar_tarefa(task_id, status)
    elif comando == "deletar" and len(sys.argv) == 3:
        task_id = sys.argv[2]
        deletar_tarefa(task_id)
    else:
        print("Comando inválido ou argumentos insuficientes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
