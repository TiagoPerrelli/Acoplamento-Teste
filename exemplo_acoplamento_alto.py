"""
EXEMPLO 4: Sistema Monolítico com Alto Acoplamento (Antipadrão)
==============================================================

Um exemplo de CÓDIGO RUIM com alto acoplamento que você
NÃO deve usar, mas é útil ver para aprender a identificar problemas.
"""

# ============================================================================
# ANTIPADRÃO: Código com Alto Acoplamento (NÃO USE EM PRODUÇÃO!)
# ============================================================================

class GlobalState:
    """Variáveis globais - ANTIPADRÃO!"""
    config = {}
    cache = {}
    errors = []
    users = []
    products = []
    orders = []


class UserManager:
    """Gerencia usuários com alto acoplamento"""
    
    def add_user(self, name, email):
        """Adiciona usuário - modifica estado global"""
        user = {'name': name, 'email': email}
        GlobalState.users.append(user)
        # ← Modifica GlobalState diretamente!
        GlobalState.cache['last_user'] = user
        # ← Também modifica cache global!
        return user
    
    def get_all_users(self):
        """Obtém todos os usuários - lê estado global"""
        # ← Lê GlobalState
        return GlobalState.users
    
    def validate_email(self, email):
        """Valida email - mas precisa ler config global"""
        # ← Depende de GlobalState.config
        if not GlobalState.config.get('validate_email'):
            return True
        
        return '@' in email
    
    def send_welcome_email(self, user):
        """Envia email - mas precisa de configurações globais"""
        # ← Acoplado com GlobalState.config
        smtp_server = GlobalState.config.get('smtp_server')
        if not smtp_server:
            GlobalState.errors.append("SMTP não configurado")
            # ← Também escreve em GlobalState.errors
            return False
        
        print(f"Email enviado para {user['email']}")
        return True


class ProductManager:
    """Gerencia produtos - TAMBÉM com alto acoplamento"""
    
    def add_product(self, name, price):
        """Adiciona produto - modifica estado global"""
        product = {'name': name, 'price': price}
        GlobalState.products.append(product)
        # ← Modifica GlobalState diretamente!
        return product
    
    def get_product(self, product_id):
        """Obtém produto - lê estado global"""
        # ← Lê GlobalState
        if product_id < len(GlobalState.products):
            return GlobalState.products[product_id]
        return None
    
    def calculate_tax(self, product):
        """Calcula imposto - depende de configuração global"""
        # ← Acoplado com GlobalState.config
        tax_rate = GlobalState.config.get('tax_rate', 0.1)
        return product['price'] * tax_rate
    
    def update_cache(self, product):
        """Atualiza cache - modifica GlobalState"""
        # ← Também modifica GlobalState.cache
        GlobalState.cache[f"product_{product['name']}"] = product


class OrderManager:
    """Gerencia pedidos - PIOR caso de acoplamento"""
    
    def __init__(self):
        self.user_manager = UserManager()
        # ← ACOPLAMENTO: depende de UserManager
        self.product_manager = ProductManager()
        # ← ACOPLAMENTO: depende de ProductManager
    
    def create_order(self, user_id, product_id):
        """Cria pedido - altamente acoplado"""
        
        # Obtém usuário
        users = self.user_manager.get_all_users()
        # ← Chama UserManager
        if user_id >= len(users):
            GlobalState.errors.append("Usuário não encontrado")
            # ← Modifica GlobalState.errors
            return None
        
        user = users[user_id]
        
        # Obtém produto
        product = self.product_manager.get_product(product_id)
        # ← Chama ProductManager
        if not product:
            GlobalState.errors.append("Produto não encontrado")
            # ← Modifica GlobalState.errors novamente
            return None
        
        # Calcula imposto
        tax = self.product_manager.calculate_tax(product)
        # ← Chama ProductManager novamente
        
        # Calcula total
        total = product['price'] + tax
        
        # Cria pedido
        order = {
            'user': user,
            'product': product,
            'total': total,
            'status': 'pending'
        }
        
        GlobalState.orders.append(order)
        # ← Modifica GlobalState.orders
        
        # Atualiza cache
        self.product_manager.update_cache(product)
        # ← Chama ProductManager para atualizar cache
        
        # Envia email de confirmação
        self.user_manager.send_welcome_email(user)
        # ← Chama UserManager para enviar email
        
        # Atualiza configuração??
        GlobalState.config['last_order_id'] = len(GlobalState.orders)
        # ← Modifica config global (???)
        
        return order
    
    def get_all_orders(self):
        """Obtém todos os pedidos - lê estado global"""
        # ← Lê GlobalState.orders
        return GlobalState.orders
    
    def get_order_summary(self):
        """Gera resumo - depende de TUDO"""
        orders = self.get_all_orders()
        # ← Lê GlobalState.orders
        users = self.user_manager.get_all_users()
        # ← Lê através de UserManager que lê GlobalState
        products = GlobalState.products
        # ← Lê GlobalState.products
        
        return {
            'total_orders': len(orders),
            'total_users': len(users),
            'total_products': len(products),
            'errors': len(GlobalState.errors)
            # ← Lê GlobalState.errors
        }


class ReportGenerator:
    """Gera relatórios - também acoplado demais"""
    
    def __init__(self):
        self.order_manager = OrderManager()
        # ← ACOPLAMENTO: depende de OrderManager
    
    def generate_sales_report(self):
        """Gera relatório de vendas"""
        
        orders = self.order_manager.get_all_orders()
        # ← Lê através de OrderManager que lê GlobalState
        
        if not orders:
            GlobalState.errors.append("Nenhum pedido para gerar relatório")
            # ← Modifica GlobalState.errors
            return None
        
        summary = self.order_manager.get_order_summary()
        # ← Chama OrderManager
        
        report = f"""
        RELATÓRIO DE VENDAS
        ==================
        Total de Pedidos: {summary['total_orders']}
        Total de Usuários: {summary['total_users']}
        Total de Produtos: {summary['total_products']}
        Erros: {summary['errors']}
        
        Cache Size: {len(GlobalState.cache)}
        """
        
        # Salva em cache
        GlobalState.cache['last_report'] = report
        # ← Modifica GlobalState.cache
        
        return report
    
    def print_report(self):
        """Imprime relatório"""
        report = self.generate_sales_report()
        if report:
            print(report)


# ============================================================================
# USO - Demonstração dos problemas
# ============================================================================

def main():
    """Uso do sistema acoplado"""
    
    # Configurar
    GlobalState.config['validate_email'] = True
    GlobalState.config['tax_rate'] = 0.1
    GlobalState.config['smtp_server'] = 'smtp.example.com'
    
    # Criar gerenciadores
    user_mgr = UserManager()
    product_mgr = ProductManager()
    order_mgr = OrderManager()
    report_gen = ReportGenerator()
    
    # Adicionar usuário
    user = user_mgr.add_user("João", "joao@email.com")
    print(f"Usuário adicionado: {user}")
    
    # Adicionar produto
    product = product_mgr.add_product("Notebook", 2000.00)
    print(f"Produto adicionado: {product}")
    
    # Criar pedido
    order = order_mgr.create_order(0, 0)
    print(f"Pedido criado: {order}")
    
    # Gerar relatório
    report_gen.print_report()
    
    # Ver estado global (BAD!)
    print(f"\nEstado Global (ANTIPADRÃO!):")
    print(f"  Usuários: {GlobalState.users}")
    print(f"  Produtos: {GlobalState.products}")
    print(f"  Pedidos: {GlobalState.orders}")
    print(f"  Cache: {GlobalState.cache}")
    print(f"  Erros: {GlobalState.errors}")


# ============================================================================
# ANÁLISE ESPERADA - PROBLEMAS
# ============================================================================

"""
PROBLEMAS DETECTADOS (MUITOS!):

[1] Variáveis Globais
    ❌ GlobalState.config, .cache, .errors, .users, .products, .orders
    ❌ Qualquer classe pode modificar QUALQUER coisa
    ❌ Impossível rastrear quem modificou o quê
    ❌ Testes não conseguem isolar comportamento

[2] Acoplamento Direto com GlobalState
    ❌ UserManager → GlobalState (múltiplos acessos)
    ❌ ProductManager → GlobalState (múltiplos acessos)
    ❌ OrderManager → GlobalState (múltiplos acessos)
    ❌ ReportGenerator → GlobalState (múltiplos acessos)

[3] Acoplamento entre Classes
    ❌ OrderManager → UserManager (cria instância)
    ❌ OrderManager → ProductManager (cria instância)
    ❌ ReportGenerator → OrderManager (cria instância)
    ❌ Difícil testar sem testar tudo

[4] Responsabilidades Misturadas
    ❌ UserManager: adiciona, valida, envia email
    ❌ ProductManager: calcula imposto, atualiza cache
    ❌ OrderManager: cria, envia email, atualiza cache
    ❌ ReportGenerator: gera, salva em cache

[5] Efeitos Colaterais Ocultos
    ❌ create_order() modifica: GlobalState.orders, .errors, .cache, .config
    ❌ Impossível prever todas as consequências
    ❌ Uma mudança quebra tudo

ÍNDICE DE COESÃO ESPERADO: -50% a -100% (PÉSSIMO!)
    Motivo: Altíssimo acoplamento com estado global

ACOPLAMENTOS CRÍTICOS:
    🔴 OrderManager → UserManager (obrigatório)
    🔴 OrderManager → ProductManager (obrigatório)
    🔴 ReportGenerator → OrderManager (obrigatório)
    🔴 TODAS as classes → GlobalState (PÉSSIMO!)

COMO REFATORAR:
    1. Remover GlobalState
    2. Usar Dependency Injection
    3. Usar Interfaces/Protocolos
    4. Separar responsabilidades
    5. Ver: exemplo_desacoplado.py
"""

if __name__ == "__main__":
    main()
