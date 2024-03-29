from getpass import getpass

from werkzeug.security import generate_password_hash

from . import app, db
from .models import CategoryPage, Page, PaymentMethod, Role, Route, User


@app.cli.command("initdb")
def init_db():
    """
    Initializes the database.
    """
    print("Initializing database...")
    db.drop_all()
    db.create_all()
    print("Database initialized.")

    # Adiciona métodos de pagameto padrão
    print("Adding default payment methods...")
    payments_method = [
        PaymentMethod(name="PIX", need_proof=True, is_payroll=False),
        PaymentMethod(name="Cartão de Crédito", need_proof=False, is_payroll=False),
        PaymentMethod(name="Cartão de Debito", need_proof=False, is_payroll=False),
        PaymentMethod(name="Espécie", need_proof=False, is_payroll=False),
        PaymentMethod(name="Folha de Pagamento", need_proof=False, is_payroll=True),
        PaymentMethod(name="System", need_proof=False, is_payroll=False, is_protected=True),
    ]
    db.session.add_all(payments_method)
    db.session.commit()

    # Adiciona rotas padrão
    print("Adding default routes...")
    routes = [
        Route(id=1, name="Arquivos estáticos", endpoint="static"),
        Route(id=2, name="Login", endpoint="login"),
        Route(id=3, name="Logout", endpoint="logout"),
        Route(id=4, name="Home", endpoint="index"),
        Route(id=5, name="Cantina", endpoint="cantina"),
        Route(
            id=6,
            name="Confirmar Compra",
            endpoint="confirm_purchase",
            block_recurring_access=True,
        ),
        Route(
            id=7,
            name="Produtos para Despache",
            endpoint="products_for_despache",
        ),
        Route(id=8, name="Perfil", endpoint="profile"),
        Route(id=9, name="Editar Perfil", endpoint="edit_profile"),
        Route(id=10, name="Editar Senha", endpoint="edit_password"),
        Route(id=11, name="Usuários", endpoint="users"),
        Route(id=12, name="Recarregar", endpoint="recharge"),
        Route(id=13, name="Histórico de Pagamentos", endpoint="payments_history"),
        Route(id=14, name="Produtos", endpoint="products"),
        Route(id=15, name="Verificação de Pagamentos", endpoint="verify_payments"),
        Route(id=16, name="Controle de Estoque", endpoint="stock_control"),
        Route(
            id=17,
            name="Histórico de Entrada do Estoque",
            endpoint="stock_history",
        ),
        Route(id=18, name="Editar Produto", endpoint="edit_product"),
        Route(id=19, name="Histórico de Vendas", endpoint="sales_history"),
        Route(id=20, name="Afiliados", endpoint="affiliates"),
        Route(
            id=21,
            name="Histórico de Recarga dos Afiliados",
            endpoint="affiliates_history",
        ),
        Route(id=22, name="Filtrar Vendas de HOJE", endpoint="filter_today_sales"),
        Route(id=23, name="Pagar Saldo Devedor", endpoint="pay_payroll"),
        Route(
            id=24,
            name="Histórico de Edição de Produtos",
            endpoint="history_edits_products",
        ),
        Route(
            id=25,
            name="Histórico de Edição de Usuários",
            endpoint="history_edits_users",
        ),
        Route(
            id=26,
            name="Usuários com Saldo Disponível",
            endpoint="users_with_balance",
        ),
        Route(
            id=27,
            name="(API) Adicionar ao carrinho",
            endpoint="add_to_cart_api",
            block_recurring_access=True,
        ),
        Route(
            id=28,
            name="(API) Remover do carrinho",
            endpoint="remove_from_cart_api",
            block_recurring_access=True,
        ),
        Route(id=29, name="(API) Obter Usuário", endpoint="get_user_api"),
        Route(
            id=30,
            name="(API) Gerar Nome de Usuário Aleatório",
            endpoint="generate_random_username_api",
        ),
        Route(id=31, name="(API) Obter pagamentos", endpoint="get_payments_api"),
        Route(
            id=32,
            name="(API) Verificar pagamento",
            endpoint="verify_payment_api",
            block_recurring_access=True,
        ),
        Route(
            id=33,
            name="(API) Exportar para Excel",
            endpoint="export_to_excel_api",
        ),
        Route(
            id=34,
            name="(API) Listar Produtos para Despacho",
            endpoint="list_users_pending_desp_api",
        ),
        Route(
            id=35,
            name="(API) Confirmar Produto Despachado",
            endpoint="confirm_despache_api",
            block_recurring_access=True,
        ),
        Route(id=36, name="(ADMIN) Rotas", endpoint="routes"),
        Route(
            id=37,
            name="(ADMIN) Categoria das Páginas",
            endpoint="category_pages",
        ),
        Route(id=38, name="(ADMIN) Cargos", endpoint="roles"),
        Route(id=39, name="(ADMIN) Páginas", endpoint="pages"),
        Route(
            id=40,
            name="(API) Despachar todos os produtos de todos os usuários",
            endpoint="confirm_all_despaches_api",
            block_recurring_access=True,
        ),
        Route(
            id=41,
            name="(API) Despachar todos os produtos de um usuário",
            endpoint="confirm_all_user_despaches_api",
            block_recurring_access=True,
        ),
        Route(
            id=42,
            name="(API) Listar produtos para despacho de um usuário",
            endpoint="list_user_despaches_api",
        ),
        Route(
            id=43,
            name="Usuários com Saldo Devedor",
            endpoint="users_with_balance_payroll",
        ),
        Route(
            id=44,
            name="Checkout Folha de Pagamento",
            endpoint="checkout_payroll",
        ),
    ]
    db.session.add_all(routes)
    db.session.commit()

    # Adiciona Categorias de Páginas Padrão
    print("Adding default categories...")
    categories = [
        CategoryPage(
            name="Geral",
            description="Páginas referentes à funcionalidades Gerais",
        ),
        CategoryPage(
            name="Cantina",
            description="Páginas referentes à funcionalidades da Cantina",
        ),
        CategoryPage(
            name="Auditorias",
            description="Páginas referentes a auditoria em geral",
        ),
        CategoryPage(
            name="Administração",
            description="Páginas referentes à funcionalidades do Administrador",
        ),
    ]
    db.session.add_all(categories)
    db.session.commit()

    # Adiciona as Páginas Padrões
    print("Adding default pages...")
    pages = [
        Page(
            title="Home",
            description="Coleção de Páginas em Geral",
            route=routes[3],
            category_page=categories[0],
        ),
        Page(
            title="Meu Perfil",
            description="Referente ao seu perfil. Podes visualizar seus dados, visualizar histórico de transações e recargas, etc.",
            route=routes[7],
            category_page=categories[0],
            appear_navbar=True,
        ),
        Page(
            title="Recarga",
            description="Aqui você pode solicitar recargas especificando o valor e o método de pagamento.",
            route=routes[11],
            category_page=categories[1],
            appear_navbar=True,
        ),
        Page(
            title="Histórico de Pagamentos",
            description="Aqui você pode visualizar o histórico de pagamentos feito pelos usuários em geral, tendo a possibilidade de exportar para excel, filtrar por data, usuário e forma de pagamento.",
            route=routes[12],
            category_page=categories[2],
        ),
        Page(
            title="Cantina",
            description="Página refernte à Venda de Produtos da Cantina.",
            route=routes[4],
            category_page=categories[1],
            appear_navbar=True,
        ),
        Page(
            title="Produtos para Despache",
            description="Referente ao despache de produtos que foram vendidos.",
            route=routes[6],
            category_page=categories[1],
        ),
        Page(
            title="Histórico de Vendas",
            description="Aqui você pode visualizar o histórico de vendas feito pelos usuários em geral, tendo a possibilidade de exportar para excel, fazer filtro por data e usuário.",
            route=routes[18],
            category_page=categories[2],
        ),
        Page(
            title="Produtos da Cantina",
            description="Aqui você pode pode visualizar uma lista de produtos com possibilidade de os editar.",
            route=routes[13],
            category_page=categories[1],
            appear_navbar=True,
        ),
        Page(
            title="Adicionar Produto",
            description="Aqui você pode cadastrar um determinado produto ao estoque da cantina informando quantidade e valor de compra.",
            route=routes[15],
            category_page=categories[1],
        ),
        Page(
            title="Histórico de Entrada do Estoque",
            description="Aqui você pode visualizar o histórico de cadastro de produtos no estoque com possibilidade de exportar para excel, filtrar por data e usuário.",
            route=routes[16],
            category_page=categories[2],
        ),
        Page(
            title="Histórico de Edição de Produtos",
            description="Aqui você pode visualizar o histórico de edição de produtos com possibilidade de exportar para excel, filtrar por data, usuário e produto.",
            route=routes[23],
            category_page=categories[2],
        ),
        Page(
            title="Usuários",
            description="Referente à pagina de usuários onde se é possível adicionar, visualizar, editar e remover usuários.",
            route=routes[10],
            category_page=categories[0],
            appear_navbar=True,
        ),
        Page(
            title="Histórico de Edição de Usuários",
            description="Aqui você pode visualizar o histórico de edição de usuários com possibilidade de exportar para excel, filtrar por data, usuário (tando usuário quanto usuário que editou).",
            route=routes[24],
            category_page=categories[2],
        ),
        Page(
            title="Verificação de Pagamentos",
            description="Página para verificação de solicitação de recargas feitas pelos usuários em geral com possibilidade de liberar, rejeitar e ver comprovante de recargas.",
            route=routes[14],
            category_page=categories[1],
            appear_navbar=True,
        ),
        Page(
            title="Afiliados",
            description="Aqui você pode gerenciar seus afiliados.",
            route=routes[19],
            category_page=categories[0],
            appear_navbar=True,
        ),
        Page(
            title="Histórico de Recarga dos Afiliados",
            description="Aqui você pode visualizar o histórico de recargas dos afiliados onde podes filtrar por data.",
            route=routes[20],
            category_page=categories[2],
        ),
        Page(
            title="Pagar Saldo Devedor",
            description="Aqui você pode fazer o pagamento da folha de pagamento, ou seja, o que acumulou durante um determinado período.",
            route=routes[22],
            category_page=categories[0],
        ),
        Page(
            title="Sair",
            description="Sair do Sistema",
            route=routes[2],
            category_page=categories[0],
            appear_navbar=True,
        ),
        Page(
            title="Usuários com Saldo Disponível",
            description="Aqui você pode visualizar os usuários que tem saldo disponível, ou seja, usuários cujo saldo é maior que zero.",
            route=routes[25],
            category_page=categories[2],
        ),
        Page(
            title="Rotas",
            description="Aqui você pode visualizar as rotas do sistema bem como alterar seus nomes.",
            route=routes[35],
            category_page=categories[3],
        ),
        Page(
            title="Gerenciamento das Categorias das Páginas",
            description="Aqui você pode gerenciar nome e descrição das categorias das páginas (essas que sã o apresentadas na página inicial).",
            route=routes[36],
            category_page=categories[3],
        ),
        Page(
            title="Gerenciamento de Cargos",
            description="Gerenciamento de Cargos :p",
            route=routes[37],
            category_page=categories[3],
        ),
        Page(
            title="Gerenciamento das Páginas",
            description="Gerenciamento das Páginas",
            route=routes[38],
            category_page=categories[3],
        ),
        Page(
            title="Usuários com Saldo Devedor",
            description="Visualização dos usuários com saldo devedor maior que zero.",
            route=routes[42],
            category_page=categories[3],
        ),
        Page(
            title="Checkout Folha de Pagamento",
            description="Permite debitar a folha de pagamento dos usuários.",
            route=routes[43],
            category_page=categories[3],
        ),
    ]
    db.session.add_all(pages)
    db.session.commit()

    # Adiciona os Cargos Padrões
    print("Adding default roles...")
    import json

    roles = [
        Role(
            name="Admin",
            description="Administrador do Site :P (#GOD)",
            allowed_routes=json.dumps(list(range(1, len(routes) + 1))),
        ),
        Role(
            name="Funcionário",
            description="Funcionários em Geral no Site (Professores, Coordenadores, etc.)",
            allowed_routes=json.dumps([1, 2, 3, 4, 8, 10, 20, 21, 12, 14, 23]),
        ),
        Role(
            name="Aluno",
            description="Alunos da Escola",
            allowed_routes=json.dumps([1, 2, 3, 4, 8, 10, 12, 14, 27, 28, 5, 6]),
        ),
        Role(
            name="Caixa",
            description="Caixas da Cantina",
            allowed_routes=json.dumps(
                [
                    1,
                    2,
                    3,
                    4,
                    8,
                    10,
                    12,
                    15,
                    20,
                    21,
                    23,
                    17,
                    22,
                    19,
                    13,
                    14,
                    5,
                    6,
                    31,
                    32,
                    33,
                    27,
                    28,
                ]
            ),
        ),
        Role(
            name="Guest",
            description="Visitante (ignore)",
            allowed_routes=json.dumps([1, 2]),
        ),
    ]
    db.session.add_all(roles)
    db.session.commit()
    print("Already created.")


@app.cli.command("createsuperuser")
def create_superuser():
    """
    Creates a superuser.
    """
    print("Creating superuser...")
    role = Role.query.get(1)  # admin :D // Role.query.filter_by(name="Admin").first()
    print("Insert the username and password for superuser: ")
    username = input("Username: ")
    while True:
        password = getpass("Password: ")
        if password == "":
            print("Password cannot be empty.")
            continue
        confimation_password = getpass("Confirm password: ")
        if password != confimation_password:
            print("Passwords do not match.")
            continue
        break
    superuser = User(
        name=username.capitalize(),
        username=username,
        password=generate_password_hash(password),
        role=role,
    )
    db.session.add(superuser)
    db.session.commit()
    print("Superuser created.")
