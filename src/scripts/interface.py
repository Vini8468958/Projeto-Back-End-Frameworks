# Importa o nosso outro arquivo, o api_client, como se fosse uma biblioteca
import cliente 

def exibir_lista_tarefas():
    """Chama a função da API e exibe o resultado para o utilizador."""
    print("\nA procurar tarefas...")
    tarefas = cliente.listar_tarefas()
    
    if tarefas is not None:
        if not tarefas:
            print("Nenhuma tarefa encontrada.")
        else:
            print("\n--- Lista de Tarefas ---")
            for tarefa in tarefas:
                print(f"ID: {tarefa['id']}, Título: {tarefa['titulo']}, Estado: {tarefa['status']}")
            print("------------------------")

def adicionar_nova_tarefa():
    """Pede os dados ao utilizador e chama a função da API para criar a tarefa."""
    print("\n--- Criar Nova Tarefa ---")
    titulo = input("Digite o título da tarefa: ")
    descricao = input("Digite a descrição (opcional): ")

    response = cliente.criar_tarefa(titulo, descricao)

    if response and response.status_code == 201:
        print("Tarefa criada com sucesso!")
    else:
        print("Falha ao criar a tarefa.")

def remover_tarefa():
    """Pede o ID ao utilizador e chama a função da API para apagar a tarefa."""
    try:
        task_id = int(input("\nDigite o ID da tarefa que deseja apagar: "))
    except ValueError:
        print("ID inválido. Por favor, digite um número.")
        return

    response = cliente.deletar_tarefa(task_id)
    
    if response and response.status_code == 204:
        print(f"Tarefa com ID {task_id} apagada com sucesso!")
    elif response and response.status_code == 404:
         print(f"Erro: Tarefa com ID {task_id} não encontrada.")
    else:
        print("Falha ao apagar a tarefa.")

def menu_principal():
    """Exibe o menu principal e gere a entrada do utilizador."""
    while True:
        print("\n--- Sistema de Gestão de Tarefas ---")
        print("1. Listar todas as tarefas")
        print("2. Criar uma nova tarefa")
        print("3. Apagar uma tarefa")
        print("4. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            exibir_lista_tarefas()
        elif escolha == '2':
            adicionar_nova_tarefa()
        elif escolha == '3':
            remover_tarefa()
        elif escolha == '4':
            print("A sair...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Este é o ponto de partida do nosso programa
if __name__ == "__main__":
    menu_principal()
