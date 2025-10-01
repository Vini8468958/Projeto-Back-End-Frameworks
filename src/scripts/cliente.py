import requests
import json
from datetime import datetime

# colocar link novo sempre que ligar o servidor
BASE_URL = "https://d500f82e0dc0.ngrok-free.app" 

HEADERS = {"ngrok-skip-browser-warning": "true"}


def listar_tarefas():

    #GET
    print("\n[INFO] Tentando buscar todas as tarefas...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=HEADERS)
        response.raise_for_status() 
        if response.text:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        print(f"\n[ERRO] Não foi possível conectar ao servidor. Verifique se o backend está rodando em: {BASE_URL}")
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")
    return None

def visualizar_tarefa(task_id):
    #GET BY ID
    print(f"\n[INFO] Tentando buscar tarefa com ID: {task_id}...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[AVISO] Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")
    return None

def criar_tarefa(titulo, descricao):
    
    #POST

    print("\n[INFO] Tentando criar nova tarefa...")
    nova_tarefa = {"titulo": titulo, "descricao": descricao}
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=nova_tarefa, headers=HEADERS)
        if response.status_code == 201:
            print(f"\n[SUCESSO] Tarefa '{titulo}' criada com sucesso! ID: {response.json().get('id')}")
        elif response.status_code == 400:
            print(f"[ERRO] Falha ao criar tarefa. Dados inválidos: {response.json().get('erro', 'Sem detalhes')}")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")

def atualizar_tarefa(task_id, novo_titulo, nova_descricao, novo_status):
    
    #UPTADE OU PUT

    print(f"\n[INFO] Tentando atualizar tarefa com ID: {task_id}...")
    dados_atualizados = {
        "titulo": novo_titulo, 
        "descricao": nova_descricao,
        "status": novo_status
    }
    try:
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=dados_atualizados, headers=HEADERS)
        if response.status_code == 200:
            print(f"\n[SUCESSO] Tarefa ID {task_id} atualizada com sucesso!")
        elif response.status_code == 404:
            print(f"[ERRO] Não foi possível atualizar. Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")

def deletar_tarefa(task_id):
    
    #DELETE

    print(f"\n[INFO] Tentando deletar tarefa com ID: {task_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=HEADERS)
        if response.status_code == 204:
            print(f"\n[SUCESSO] Tarefa ID {task_id} deletada com sucesso!")
        elif response.status_code == 404:
            print(f"[ERRO] Não foi possível deletar. Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")


# INTERFACE

def exibir_tarefas(tarefas):
    """Exibe a lista de tarefas de forma formatada."""
    if tarefas is None:
        return
    if not tarefas:
        print("\nLista de tarefas vazia.")
        return

    print("\n" + "="*50)
    print("                   LISTA DE TAREFAS")
    print("="*50)
    
    for t in tarefas:
        status_display = f"[{t.get('status', 'N/A').upper()}]"
        try:
            data_criacao = datetime.fromtimestamp(t['criado_em']).strftime('%Y-%m-%d %H:%M') if t['criado_em'] else "N/A"
        except (TypeError, ValueError):
            data_criacao = "Data inválida"
            
        print(f"ID: {t['id']} | {status_display}")
        print(f"Título: {t['titulo']}")
        print(f"Criado em: {data_criacao}")
        print("-" * 50)

def menu_criar():
    print("\n--- CRIAR NOVA TAREFA ---")
    titulo = input("Título (obrigatório): ").strip()
    if not titulo:
        print("[AVISO] O título não pode ser vazio.")
        return
    descricao = input("Descrição (opcional): ").strip()
    criar_tarefa(titulo, descricao)

def menu_visualizar():
    print("\n--- VISUALIZAR TAREFA ---")
    try:
        task_id = int(input("ID da tarefa para visualizar: "))
    except ValueError:
        print("[ERRO] O ID deve ser um número inteiro.")
        return
    tarefa = visualizar_tarefa(task_id)
    if tarefa:
        print("\n" + "#"*40)
        print(f"   DETALHES DA TAREFA ID: {tarefa['id']}")
        print("#"*40)
        print(f"Título: {tarefa['titulo']}")
        print(f"Descrição: {tarefa.get('descricao', '(Sem descrição)')}")
        print(f"Status: {tarefa['status'].upper()}")
        data_criacao = datetime.fromtimestamp(tarefa['criado_em']).strftime('%Y-%m-%d %H:%M') if tarefa['criado_em'] else "N/A"
        print(f"Criado em: {data_criacao}")
        print("#"*40)

def menu_atualizar():
    print("\n--- ATUALIZAR TAREFA ---")
    try:
        task_id = int(input("ID da tarefa para atualizar: "))
    except ValueError:
        print("[ERRO] O ID deve ser um número inteiro.")
        return
    
    tarefa_atual = visualizar_tarefa(task_id)
    if not tarefa_atual:
        return
    
    print(f"\n[INFO] Atualizando a tarefa '{tarefa_atual['titulo']}' (Deixe em branco para manter o valor atual)")
    
    novo_titulo = input(f"Novo Título (Atual: {tarefa_atual['titulo']}): ").strip() or tarefa_atual['titulo']
    nova_descricao = input(f"Nova Descrição (Atual: {tarefa_atual.get('descricao', '')}): ").strip() or tarefa_atual.get('descricao', '')
    
    novo_status = input(f"Novo Status (Atual: {tarefa_atual['status']}). Digite 'pendente' ou 'concluída': ").strip().lower()
    if novo_status not in ['pendente', 'concluída']:
        print(f"[AVISO] Status inválido ou vazio. Mantendo status atual: '{tarefa_atual['status']}'")
        novo_status = tarefa_atual['status']
        
    atualizar_tarefa(task_id, novo_titulo, nova_descricao, novo_status)

def menu_deletar():
    print("\n--- DELETAR TAREFA ---")
    try:
        task_id = int(input("ID da tarefa para deletar: "))
    except ValueError:
        print("[ERRO] O ID deve ser um número inteiro.")
        return
    
    confirmacao = input(f"Tem certeza que deseja deletar a tarefa ID {task_id}? (s/n): ").lower()
    if confirmacao == 's':
        deletar_tarefa(task_id)
    else:
        print("[AVISO] Operação de deleção cancelada.")




def exibir_menu():
    print("\n" + "="*30)
    print("   SISTEMA DE GESTÃO DE TAREFAS")
    print("="*30)
    print("1. Listar todas as tarefas")
    print("2. Visualizar tarefa por ID")
    print("3. Criar nova tarefa")
    print("4. Atualizar tarefa")
    print("5. Deletar tarefa")
    print("0. Sair")
    print("="*30)

def main():
    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            exibir_tarefas(listar_tarefas())
        elif escolha == '2':
            menu_visualizar()
        elif escolha == '3':
            menu_criar()
        elif escolha == '4':
            menu_atualizar()
        elif escolha == '5':
            menu_deletar()
        elif escolha == '0':
            print("Saindo do Cliente. Até logo!")
            break
        else:
            print("[AVISO] Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
