import requests
import json
from datetime import datetime

# A URL base do seu servidor backend
BASE_URL = "http://localhost:8000"  # Sugiro usar localhost se o servidor estiver local
# BASE_URL = "https://6f1a66231bbd.ngrok-free.app" 

# Cabeçalho especial para ignorar o aviso do ngrok, se estiver usando ngrok
HEADERS = {"ngrok-skip-browser-warning": "true"}


# ## 1. FUNÇÕES DE COMUNICAÇÃO (CRUD) 


def listar_tarefas():
    """Faz a requisição GET para buscar todas as tarefas."""
    print("\n[INFO] Tentando buscar todas as tarefas...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=HEADERS)
        
        # O response.raise_for_status() trata 4xx e 5xx como exceção.
        # Se for 200 (OK), a execução continua.
        response.raise_for_status() 
        
        # Verifica se a resposta não está vazia ou é válida para JSON
        if response.text:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        print("\n[ERRO] Não foi possível conectar ao servidor. Verifique se o backend está rodando em:", BASE_URL)
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")
    return None

def visualizar_tarefa(task_id):
    """[NOVA FUNÇÃO] Faz a requisição GET para buscar UMA tarefa específica."""
    print(f"\n[INFO] Tentando buscar tarefa com ID: {task_id}...")
    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=HEADERS)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[ERRO] Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")
    return None

def criar_tarefa(titulo, descricao):
    """Faz a requisição POST para criar uma nova tarefa."""
    print("\n[INFO] Tentando criar nova tarefa...")
    nova_tarefa = {"titulo": titulo, "descricao": descricao}
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=nova_tarefa, headers=HEADERS)
        
        if response.status_code == 201: # 201 Created é o esperado para POST
            print(f"\n[SUCESSO] Tarefa '{titulo}' criada com sucesso! ID: {response.json().get('id')}")
        elif response.status_code == 400: # 400 Bad Request (ex: título vazio)
            print(f"[ERRO] Falha ao criar tarefa. Dados inválidos: {response.json().get('message', 'Sem detalhes')}")
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")

def atualizar_tarefa(task_id, novo_titulo, nova_descricao, novo_status):
    """[NOVA FUNÇÃO] Faz a requisição PUT para atualizar uma tarefa existente."""
    print(f"\n[INFO] Tentando atualizar tarefa com ID: {task_id}...")
    dados_atualizados = {
        "titulo": novo_titulo, 
        "descricao": nova_descricao,
        "status": novo_status
    }
    
    try:
        response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=dados_atualizados, headers=HEADERS)
        
        if response.status_code == 200: # 200 OK é o esperado para PUT
            print(f"\n[SUCESSO] Tarefa ID {task_id} atualizada com sucesso!")
        elif response.status_code == 404:
            print(f"[ERRO] Não foi possível atualizar. Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")

def deletar_tarefa(task_id):
    """Faz a requisição DELETE para remover uma tarefa."""
    print(f"\n[INFO] Tentando deletar tarefa com ID: {task_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=HEADERS)
        
        if response.status_code == 204: # 204 No Content é o esperado para DELETE
            print(f"\n[SUCESSO] Tarefa ID {task_id} deletada com sucesso!")
        elif response.status_code == 404:
            print(f"[ERRO] Não foi possível deletar. Tarefa com ID {task_id} não encontrada.")
        else:
            response.raise_for_status()
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na requisição: {e}")


# ## 2. FUNÇÕES DA INTERFACE (USER INTERFACE) ##


def exibir_tarefas(tarefas):
    """Exibe a lista de tarefas de forma formatada."""
    if tarefas is None:
        return
        
    if not tarefas:
        print("\nLista de tarefas vazia.")
        return

    print("\n" + "="*50)
    print("           LISTA DE TAREFAS")
    print("="*50)
    
    for t in tarefas:
        # Formatação para melhor leitura na CLI
        status_display = f"[{t['status'].upper()}]"
        
        try:
            # Tenta formatar a data, se existir
            data_criacao = datetime.fromtimestamp(t['criado_em']).strftime('%Y-%m-%d %H:%M')
        except:
            data_criacao = "Data inválida"
            
        print(f"ID: {t['id']} | {status_display}")
        print(f"Título: {t['titulo']}")
        # print(f"Descrição: {t['descricao'] if t['descricao'] else '(Sem descrição)'}")
        print(f"Criado em: {data_criacao}")
        print("-" * 50)

def menu_criar():
    """Coleta dados do usuário para criar uma tarefa."""
    print("\n--- CRIAR NOVA TAREFA ---")
    titulo = input("Título (obrigatório): ").strip()
    if not titulo:
        print("[AVISO] O título não pode ser vazio.")
        return
    descricao = input("Descrição (opcional): ").strip()
    
    criar_tarefa(titulo, descricao)

def menu_visualizar():
    """Coleta o ID e exibe os detalhes de uma tarefa."""
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
        print(f"Criado em: {datetime.fromtimestamp(tarefa['criado_em']).strftime('%Y-%m-%d %H:%M')}")
        print("#"*40)

def menu_atualizar():
    """Coleta o ID e os novos dados para atualizar uma tarefa."""
    print("\n--- ATUALIZAR TAREFA ---")
    try:
        task_id = int(input("ID da tarefa para atualizar: "))
    except ValueError:
        print("[ERRO] O ID deve ser um número inteiro.")
        return
    
    # Busca a tarefa atual para preencher os campos default
    tarefa_atual = visualizar_tarefa(task_id)
    if not tarefa_atual:
        return # Já trata o erro 404
        
    print(f"\n[INFO] Atualizando a tarefa '{tarefa_atual['titulo']}'")
    
    # Coleta novos dados (mantendo o antigo se o campo for deixado em branco)
    novo_titulo = input(f"Novo Título (Atual: {tarefa_atual['titulo']}): ").strip() or tarefa_atual['titulo']
    
    nova_descricao = input(f"Nova Descrição (Atual: {tarefa_atual.get('descricao', '')}): ").strip()
    # Se o usuário deixar vazio e tinha descrição, ele manterá a antiga.
    # Se o usuário digitar 'NULL' ou algum valor especial, caberá ao backend tratar isso.
    if not nova_descricao and 'descricao' in tarefa_atual:
        nova_descricao = tarefa_atual['descricao']

    # Permite atualizar apenas o status se o usuário quiser
    novo_status = input(f"Novo Status (Atual: {tarefa_atual['status']}). Digite 'pendente' ou 'completo': ").strip().lower()
    
    # Define o status padrão se o usuário não digitar nada ou digitar algo inválido
    if novo_status not in ['pendente', 'completo']:
        print(f"[AVISO] Status inválido ou vazio. Mantendo status atual: {tarefa_atual['status']}")
        novo_status = tarefa_atual['status']
        
    atualizar_tarefa(task_id, novo_titulo, nova_descricao, novo_status)

def menu_deletar():
    """Coleta o ID para deletar uma tarefa."""
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


# ## 3. MENU PRINCIPAL (MAIN) ##

def exibir_menu():
    """Exibe o menu de opções."""
    print("\n" + "="*30)
    print("  SISTEMA DE GESTÃO DE TAREFAS")
    print("="*30)
    print("1. Listar todas as tarefas")
    print("2. Visualizar tarefa por ID")
    print("3. Criar nova tarefa")
    print("4. Atualizar tarefa (título, descrição, status)")
    print("5. Deletar tarefa")
    print("0. Sair")
    print("="*30)

def main():
    """Função principal do Cliente CLI."""
    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            tarefas = listar_tarefas()
            exibir_tarefas(tarefas)
        elif escolha == '2':
            menu_visualizar()
        elif escolha == '3':
            menu_criar()
        elif escolha == '4':
            menu_atualizar()
        elif escolha == '5':
            menu_deletar()
        elif escolha == '0':
            print("Saindo do Cliente CLI. Até logo!")
            break
        else:
            print("[AVISO] Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()