import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        # Inicializa o cliente com o endereço fornecido e uma lista vazia de contas.
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        # Realiza uma transação na conta fornecida.
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        # Adiciona uma conta à lista de contas do cliente.
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        # Inicializa uma pessoa física com nome, data de nascimento, CPF e endereço.
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        # Inicializa uma conta com número, cliente, saldo zero, agência "0001" e um histórico vazio.
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        # Cria uma nova conta para o cliente fornecido com o número fornecido.
        return cls(numero, cliente)

    @property
    def saldo(self):
        # Retorna o saldo da conta.
        return self._saldo

    @property
    def numero(self):
        # Retorna o número da conta.
        return self._numero

    @property
    def agencia(self):
        # Retorna a agência da conta.
        return self._agencia

    @property
    def cliente(self):
        # Retorna o cliente da conta.
        return self._cliente

    @property
    def historico(self):
        # Retorna o histórico da conta.
        return self._historico

    def sacar(self, valor):
        # Realiza um saque da conta se o valor for menor ou igual ao saldo.
        saldo = self.saldo
        excedeu_saldo = valor > saldo
        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

    def depositar(self, valor):
        # Realiza um depósito na conta se o valor for maior que zero.
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            # Se o valor for menor ou igual a zero, exibe uma mensagem de erro.
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        # Inicializa uma conta corrente com número, cliente, limite e limite de saques.
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        # Realiza um saque da conta se o valor for menor ou igual ao saldo e ao limite, e se o número de saques for menor que o limite de saques.
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        # Retorna uma representação em string da conta corrente.
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        # Inicializa o histórico com uma lista vazia de transações.
        self._transacoes = []

    @property
    def transacoes(self):
        # Retorna a lista de transações do histórico.
        return self._transacoes

    def adicionar_transacao(self, transacao):
        # Adiciona uma transação ao histórico.
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        # Retorna o valor da transação.
        pass

    @abstractclassmethod
    def registrar(self, conta):
        # Registra a transação na conta.
        pass

class Saque(Transacao):
    def __init__(self, valor):
        # Inicializa um saque com o valor fornecido.
        self._valor = valor

    @property
    def valor(self):
        # Retorna o valor do saque.
        return self._valor

    def registrar(self, conta):
        # Registra o saque na conta e, se o saque for bem-sucedido, adiciona o saque ao histórico da conta.
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        # Inicializa um depósito com o valor fornecido.
        self._valor = valor

    @property
    def valor(self):
        # Retorna o valor do depósito.
        return self._valor

    def registrar(self, conta):
        # Registra o depósito na conta e, se o depósito for bem-sucedido, adiciona o depósito ao histórico da conta.
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    # Exibe o menu de opções para o usuário e retorna a opção escolhida.
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    # Filtra a lista de clientes para encontrar o cliente com o CPF informado.
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    # Retorna o cliente encontrado ou None se nenhum cliente for encontrado.
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    # Recupera a conta do cliente se o cliente tiver uma conta.
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    # Solicita ao usuário que informe o CPF do cliente.
    cpf = input("Informe o CPF do cliente: ")
    # Verifica se o cliente existe.
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    # Solicita ao usuário que informe o valor do depósito.
    valor = float(input("Informe o valor do depósito: "))
    # Cria um novo depósito com o valor fornecido.
    transacao = Deposito(valor)

    # Recupera a conta do cliente.
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # Realiza a transação de depósito na conta do cliente.
    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    # Solicita ao usuário que informe o CPF do cliente.
    cpf = input("Informe o CPF do cliente: ")
    # Verifica se o cliente existe.
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    # Solicita ao usuário que informe o valor do saque.
    valor = float(input("Informe o valor do saque: "))
    # Cria um novo saque com o valor fornecido.
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # Realiza a transação na conta do cliente.
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    # Solicita ao usuário que informe o CPF do cliente.
    cpf = input("Informe o CPF do cliente: ")
    # Verifica se o cliente existe.
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    # Recupera a conta do cliente.
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # Exibe o extrato da conta do cliente.
    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def criar_cliente(clientes):
    # Solicita ao usuário que informe o CPF do cliente.
    cpf = input("Informe o CPF (somente número): ")
    # Verifica se o cliente já existe.
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    # Solicita ao usuário que informe o nome completo, a data de nascimento e o endereço do cliente.
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    # Cria um novo cliente e adiciona à lista de clientes.
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    # Solicita ao usuário que informe o CPF do cliente.
    cpf = input("Informe o CPF do cliente: ")
    # Verifica se o cliente existe.
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    # Cria uma nova conta para o cliente e adiciona à lista de contas.
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    # Para cada conta na lista de contas, exibe as informações da conta.
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    # Inicializa as listas de clientes e contas.
    clientes = []
    contas = []

    while True:
        # Exibe o menu e obtém a opção escolhida pelo usuário.
        opcao = menu()

        if opcao == "d":
            # Se a opção for "d", realiza um depósito.
            depositar(clientes)

        elif opcao == "s":
            # Se a opção for "s", realiza um saque.
            sacar(clientes)

        elif opcao == "e":
            # Se a opção for "e", exibe o extrato.
            exibir_extrato(clientes)

        elif opcao == "nu":
            # Se a opção for "nu", cria um novo cliente.
            criar_cliente(clientes)

        elif opcao == "nc":
            # Se a opção for "nc", cria uma nova conta.
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            # Se a opção for "lc", lista as contas.
            listar_contas(contas)

        elif opcao == "q":
            # Se a opção for "q", encerra o programa.
            break

        else:
            # Se a opção não for válida, exibe uma mensagem de erro.
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

# Inicia o programa.
main()
