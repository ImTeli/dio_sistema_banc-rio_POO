from abc import ABC, abstractmethod


class Conta:
    def __init__(self, numero, cliente) -> None:
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("Erro: O valor do saque deve ser maior que zero.")
            return False
        elif valor > self.saldo:
            print("Erro: Saldo insuficiente para realizar o saque.")
            return False
        self._saldo -= valor
        print(f"Saque de R$ {valor:.2f} realizado com sucesso.")
        return True

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True
        print("Erro: O valor informado é inválido.")
        return False


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nasc, cpf, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._data_nasc = data_nasc
        self._cpf = cpf

    @property
    def cpf(self):
        return self._cpf

    @property
    def nome(self):
        return self._nome


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3) -> None:
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [tr for tr in self.historico.transacoes if tr["tipo"] == "Saque"]
        )
        if valor > self.limite:
            print(
                f"Erro: O valor do saque excede o limite máximo por saque! (R$ {self.limite})"
            )
        elif numero_saques >= self.limite_saques:
            print(
                f"Erro: O valor do saque excede o limite máximo diário de saques! ({self.limite_saques} saques.)"
            )
        else:
            return super().sacar(valor)
        return False

    def __str__(self) -> str:
        return f"""
            Agência: {self.agencia}
            Nº Conta: 00{self.numero}
            Titular: {self.cliente.nome}
        """


class Historico:
    def __init__(self) -> None:
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {"tipo": transacao.__class__.__name__, "valor": transacao.valor}
        )


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


def autenticar_cliente(clientes, cpf):
    if cpf not in [cl.cpf for cl in clientes]:
        return False
    else:
        return [cliente for cliente in clientes if cliente.cpf == cpf][0]


def menu():
    print(
        """
============== TELI BANK =============
|   Selecione a operação desejada:   |
|                                    |
|         [C] - Cadastrar Cliente    |
|         [N] - Nova Conta Corrente  |
|         [D] - Depositar            |
|         [S] - Sacar                |
|         [E] - Extrato              |
|         [L] - Listar Clientes      |
|         [Q] - Sair                 |
|                                    |
======================================
"""
    )
    return input("\n: ")


def cadastrar_cliente(clientes):
    print("\nVocê iniciou o processo de Cadastro, seja bem vindo ao Telibank!")
    cpf = input("insira o CPF do cliente: ")
    if not autenticar_cliente(clientes, cpf):
        nome = input("Digite o nome do Cliente: ")
        data_nas = input("Digite a data de nascimento do Cliente: ")
        endereco = input("Digite o endereço do cliente: ")
        clientes.append(PessoaFisica(nome, data_nas, cpf, endereco))
        print("Cliente cadastrado com Sucesso!")
    else:
        print("Erro: o CPF informado já está em uso.")


def nova_conta(n_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = (
        autenticar_cliente(clientes, cpf)
        if autenticar_cliente(clientes, cpf)
        else False
    )
    if cliente:
        conta = ContaCorrente.nova_conta(cliente, n_conta)
        contas.append(conta)
        cliente.adicionar_conta(conta)
        print(f"Sucesso: Conta de Nº 00{n_conta} criada para o cliente {cliente.nome}!")
    else:
        print("Erro: CPF informado não pertence a nenhum cliente cadastrado!")


def depositar(clientes):
    cpf = input("Digite o CPF do cliente: ")

    cliente = (
        autenticar_cliente(clientes, cpf)
        if autenticar_cliente(clientes, cpf)
        else False
    )
    if not cliente:
        print("Erro: CPF não pertence a nenhum cliente cadastrado.")
        return False
    valor = float(input("Insira do valor do depósito: "))
    transacao = Deposito(valor)

    if not cliente.contas:
        print("Erro: Cliente não possui nenhuma conta cadastrada.")
        return False
    else:
        cliente.realizar_transacao(cliente.contas[0], transacao)


def sacar(clientes):
    cpf = input("Digite o CPF do cliente: ")

    cliente = (
        autenticar_cliente(clientes, cpf)
        if autenticar_cliente(clientes, cpf)
        else False
    )
    if not cliente:
        print("Erro: CPF não pertence a nenhum cliente cadastrado.")
        return False
    
    if not cliente.contas:
        print("Erro: Cliente não possui nenhuma conta cadastrada.")
        return False
    
    valor = float(input("Insira o valor do saque: "))
    transacao = Saque(valor)

    cliente.realizar_transacao(cliente.contas[0], transacao)


def extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = [cliente for cliente in clientes if cliente.cpf == cpf][0]

    if not cliente:
        print("\nCliente não encontrado!")
        return

    conta = cliente.contas[0]
    if not conta:
        return

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


def listar_clientes(contas):
    print(" Lista de contas ".center(71,"#"))
    for conta in contas:
        print("=" * 100)
        print(str(conta))


def main_loop():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao.lower() == "c":
            cadastrar_cliente(clientes)
        elif opcao.lower() == "n":
            nova_conta(len(contas) + 1, clientes, contas)
        elif opcao.lower() == "d":
            depositar(clientes)
        elif opcao.lower() == "s":
            sacar(clientes)
        elif opcao.lower() == "e":
            extrato(clientes)
        elif opcao.lower() == "l":
            listar_clientes(contas)
        elif opcao.lower() == "q":
            print("\nObrigado por ser nosso cliente! TeliBank agradece.\n\n")
            break
        else:
            print(
                "\nOperação inválida, por favor selecione uma das opções mostradas no menu."
            )


main_loop()
