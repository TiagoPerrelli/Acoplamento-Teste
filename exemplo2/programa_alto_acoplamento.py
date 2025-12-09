#!/usr/bin/env python3
"""
🔴 PROGRAMA COM ALTO ACOPLAMENTO
Demonstração prática de um sistema com múltiplas dependências concentradas
Status: 🔴 CRÍTICO (4+ acoplamentos, ANTI-PADRÃO)
⚠️  ESTE É UM EXEMPLO DE O QUE EVITAR!
"""

# ============================================================================
# MÓDULO 1: Logger - SEM DEPENDÊNCIAS ✅ (mas será DEPENDE)
# ============================================================================

class Logger:
    """Logger simples - 0 deps próprias"""
    
    def __init__(self, name):
        self.name = name
        self.logs = []
    
    def info(self, msg):
        log_entry = f"[INFO] {self.name}: {msg}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def error(self, msg):
        log_entry = f"[ERROR] {self.name}: {msg}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def warning(self, msg):
        log_entry = f"[WARNING] {self.name}: {msg}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def get_logs(self):
        return self.logs


# ============================================================================
# MÓDULO 2: Cache - SEM DEPENDÊNCIAS ✅ (mas será DEPENDE)
# ============================================================================

class Cache:
    """Cache simples - 0 deps próprias"""
    
    def __init__(self, max_size=100):
        self.data = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key in self.data:
            self.hits += 1
            return self.data[key]
        self.misses += 1
        return None
    
    def set(self, key, value):
        if len(self.data) >= self.max_size:
            first_key = next(iter(self.data))
            del self.data[first_key]
        self.data[key] = value
    
    def clear(self):
        self.data.clear()
    
    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {'hits': self.hits, 'misses': self.misses, 'hit_rate': hit_rate}


# ============================================================================
# MÓDULO 3: Database - SEM DEPENDÊNCIAS ✅ (mas será DEPENDE)
# ============================================================================

class Database:
    """Database simples - 0 deps próprias"""
    
    def __init__(self):
        self.connection = None
        self.data = {
            1: {'id': 1, 'name': 'Alice Silva', 'email': 'alice@example.com', 'age': 28},
            2: {'id': 2, 'name': 'Bob Santos', 'email': 'bob@example.com', 'age': 35},
            3: {'id': 3, 'name': 'Carol Oliveira', 'email': 'carol@example.com', 'age': 42},
        }
    
    def connect(self):
        self.connection = "Connected"
    
    def query(self, sql):
        return []
    
    def get_user(self, user_id):
        return self.data.get(user_id)
    
    def list_users(self):
        return list(self.data.values())
    
    def insert_user(self, name, email, age):
        new_id = max(self.data.keys()) + 1
        user = {'id': new_id, 'name': name, 'email': email, 'age': age}
        self.data[new_id] = user
        return user


# ============================================================================
# MÓDULO 4: UserService - ALTO ACOPLAMENTO (3 deps HARDCODED!) 🔴
# ============================================================================

class UserService:
    """
    UserService com ALTO ACOPLAMENTO - ANTI-PADRÃO!
    
    ⚠️  PROBLEMAS:
    1. Cria suas próprias dependências (hardcoded)
    2. Impossível testar sem Logger, Cache, Database
    3. Impossível reutilizar em outro contexto
    4. Mudança em Database afeta UserService
    5. Mudança em Cache afeta UserService
    6. Mudança em Logger afeta UserService
    """
    
    def __init__(self):
        """Constructor com 3 dependências HARDCODED! 🔴"""
        # ⚠️  DEP 1: Logger
        self.logger = Logger("UserService")
        
        # ⚠️  DEP 2: Cache
        self.cache = Cache()
        
        # ⚠️  DEP 3: Database
        self.db = Database()
        self.db.connect()
        
        self.logger.info("UserService inicializado com 3 deps hardcoded")
    
    def get_user(self, user_id):
        """
        Obtém usuário com logging e cache automático
        
        Problema: Acoplado a Logger, Cache e Database
        """
        self.logger.info(f"Buscando user {user_id}")
        
        # Verificar cache
        cache_key = f'user_{user_id}'
        cached = self.cache.get(cache_key)
        if cached:
            self.logger.info(f"Cache HIT para user {user_id}")
            return cached
        
        self.logger.info(f"Cache MISS para user {user_id}")
        
        # Buscar no banco
        user = self.db.get_user(user_id)
        if user:
            self.cache.set(cache_key, user)
            self.logger.info(f"User {user_id} armazenado no cache")
        else:
            self.logger.error(f"User {user_id} não encontrado!")
        
        return user
    
    def list_users(self):
        """
        Lista todos os usuários com logging
        
        Problema: Acoplado a Logger, Cache e Database
        """
        self.logger.info("Listando todos os usuários")
        
        cache_key = 'all_users'
        cached = self.cache.get(cache_key)
        if cached:
            self.logger.info("Cache HIT para all_users")
            return cached
        
        self.logger.info("Cache MISS para all_users")
        users = self.db.list_users()
        self.cache.set(cache_key, users)
        
        self.logger.info(f"Total de {len(users)} usuários")
        return users
    
    def create_user(self, name, email, age):
        """
        Cria novo usuário com validação e logging
        
        Problema: Acoplado a Logger, Cache e Database
        """
        self.logger.info(f"Criando novo usuário: {name}")
        
        if not self._validate(name, email, age):
            self.logger.error(f"Validação falhou para {name}")
            return None
        
        user = self.db.insert_user(name, email, age)
        self.logger.info(f"Usuário criado com id {user['id']}")
        
        # Invalidar cache
        self.cache.clear()
        self.logger.info("Cache limpo após inserção")
        
        return user
    
    def update_user(self, user_id, name=None, email=None, age=None):
        """
        Atualiza usuário com logging
        
        Problema: Acoplado a Logger, Cache e Database
        """
        self.logger.info(f"Atualizando user {user_id}")
        
        if user_id not in self.db.data:
            self.logger.error(f"User {user_id} não encontrado")
            return None
        
        user = self.db.data[user_id]
        if name:
            user['name'] = name
        if email:
            user['email'] = email
        if age:
            user['age'] = age
        
        # Invalidar cache
        self.cache.delete(f'user_{user_id}') if hasattr(self.cache, 'delete') else self.cache.data.pop(f'user_{user_id}', None)
        self.logger.info(f"User {user_id} atualizado")
        
        return user
    
    def delete_user(self, user_id):
        """
        Deleta usuário com logging
        
        Problema: Acoplado a Logger, Cache e Database
        """
        self.logger.info(f"Deletando user {user_id}")
        
        if user_id in self.db.data:
            del self.db.data[user_id]
            self.cache.clear()
            self.logger.info(f"User {user_id} deletado")
            return True
        else:
            self.logger.error(f"User {user_id} não encontrado para deletar")
            return False
    
    def _validate(self, name, email, age):
        """Valida dados - ainda acoplado ao contexto"""
        if not name or len(name) < 3:
            return False
        if not email or '@' not in email:
            return False
        if not isinstance(age, int) or age < 18 or age > 150:
            return False
        return True
    
    def get_cache_stats(self):
        """Expõe stats do cache - acoplamento!"""
        return self.cache.stats()
    
    def get_logs(self):
        """Expõe logs do logger - acoplamento!"""
        return self.logger.get_logs()


# ============================================================================
# MÓDULO 5: UserHandler - MÉDIO ACOPLAMENTO (depende de UserService) 🟡
# ============================================================================

class UserHandler:
    """
    Handler HTTP que depende de UserService
    
    ⚠️  PROBLEMA: UserService já tem 3 deps, então UserHandler
    tem 4 dependências transitivas!
    """
    
    def __init__(self):
        """⚠️  Depende de UserService que tem 3 deps"""
        self.service = UserService()  # Cria UserService com suas 3 deps!
    
    def handle_get_user(self, user_id):
        """Handle GET /users/{id}"""
        user = self.service.get_user(user_id)
        if user:
            return {'status': 'success', 'data': user}
        return {'status': 'error', 'message': 'User not found'}
    
    def handle_list_users(self):
        """Handle GET /users"""
        users = self.service.list_users()
        return {'status': 'success', 'data': users, 'count': len(users)}
    
    def handle_create_user(self, name, email, age):
        """Handle POST /users"""
        user = self.service.create_user(name, email, age)
        if user:
            return {'status': 'success', 'data': user}
        return {'status': 'error', 'message': 'Invalid data'}
    
    def handle_update_user(self, user_id, **kwargs):
        """Handle PUT /users/{id}"""
        user = self.service.update_user(user_id, **kwargs)
        if user:
            return {'status': 'success', 'data': user}
        return {'status': 'error', 'message': 'User not found'}
    
    def handle_delete_user(self, user_id):
        """Handle DELETE /users/{id}"""
        success = self.service.delete_user(user_id)
        if success:
            return {'status': 'success', 'message': 'User deleted'}
        return {'status': 'error', 'message': 'User not found'}
    
    def get_diagnostics(self):
        """Expõe estado interno - acoplamento!"""
        return {
            'cache_stats': self.service.get_cache_stats(),
            'logs': self.service.get_logs()
        }


# ============================================================================
# MAIN: Demonstração dos Problemas
# ============================================================================

def main():
    """Demonstra os PROBLEMAS do ALTO acoplamento"""
    
    print("\n" + "="*80)
    print("🔴 PROGRAMA DE ALTO ACOPLAMENTO - DEMONSTRAÇÃO DE PROBLEMAS")
    print("="*80 + "\n")
    
    print("⚠️  ATENÇÃO: Este é um ANTI-PADRÃO!")
    print("Este programa mostra O QUE NÃO FAZER!\n")
    
    # ========================================================================
    # PROBLEMA 1: Criar instância é complicado
    # ========================================================================
    
    print("PROBLEMA 1: Instanciação Complexa")
    print("-" * 80)
    print("\n❌ ALTO ACOPLAMENTO:")
    print("   handler = UserHandler()  # Cria 3 deps automaticamente!")
    print("   └─ UserService()")
    print("      ├─ Logger()")
    print("      ├─ Cache()")
    print("      └─ Database()")
    print("\n✅ COMPARAÇÃO (MÉDIO ACOPLAMENTO):")
    print("   cache = Cache()")
    print("   db = Database(cache)")
    print("   service = UserService(db)")
    print("   └─ Você controla cada dependência!\n")
    
    handler = UserHandler()
    
    # ========================================================================
    # PROBLEMA 2: Testar é difícil
    # ========================================================================
    
    print("\nPROBLEMA 2: Difícil de Testar")
    print("-" * 80)
    print("\n❌ ALTO ACOPLAMENTO:")
    print("   Para testar UserService, você PRECISA:")
    print("   - Um Logger real funcionando")
    print("   - Um Cache real funcionando")
    print("   - Um Database real funcionando")
    print("   - Não pode usar mocks!")
    print("\n✅ COMPARAÇÃO (MÉDIO ACOPLAMENTO):")
    print("   class MockDB:")
    print("       def get_user(self, id): return {'id': id, 'name': 'Mock'}")
    print("   service = UserService(MockDB())  # Usa mock!")
    print("   └─ Você pode testar isoladamente!\n")
    
    # ========================================================================
    # PROBLEMA 3: Reutilização é impossível
    # ========================================================================
    
    print("\nPROBLEMA 3: Impossível Reutilizar")
    print("-" * 80)
    print("\n❌ ALTO ACOPLAMENTO:")
    print("   Quer usar UserService em outro projeto?")
    print("   - Você CARREGA Logger")
    print("   - Você CARREGA Cache")
    print("   - Você CARREGA Database")
    print("   └─ Tudo ou nada!")
    print("\n✅ COMPARAÇÃO (MÉDIO ACOPLAMENTO):")
    print("   Quer usar Database em outro projeto?")
    print("   - Você passa qualquer Cache")
    print("   - Você passa qualquer Database")
    print("   └─ Máxima flexibilidade!\n")
    
    # ========================================================================
    # PROBLEMA 4: Mudanças quebram tudo
    # ========================================================================
    
    print("\nPROBLEMA 4: Mudanças Quebram Tudo")
    print("-" * 80)
    print("\n❌ ALTO ACOPLAMENTO:")
    print("   Se você mudar Logger:")
    print("   - UserService quebra")
    print("   - UserHandler quebra")
    print("   - Todos que usam UserService quebram")
    print("\n❌ Se você mudar Cache:")
    print("   - UserService quebra")
    print("   - UserHandler quebra")
    print("\n❌ Se você mudar Database:")
    print("   - UserService quebra")
    print("   - UserHandler quebra")
    print("\n✅ COMPARAÇÃO (MÉDIO ACOPLAMENTO):")
    print("   Se você mudar Logger:")
    print("   - Ninguém quebra (Logger é independente)")
    print("   Se você mudar Cache:")
    print("   - Database pode quebrar (usa Cache)")
    print("   - Mas UserService não quebra (não depende direto)")
    print("\n")
    
    # ========================================================================
    # DEMONSTRAÇÃO: Operações
    # ========================================================================
    
    print("\nDEMONSTRAÇÃO: Executando Operações")
    print("-" * 80 + "\n")
    
    # Buscar usuário
    print("1️⃣ Buscando user 1:")
    response = handler.handle_get_user(1)
    print(f"   Resultado: {response['data']['name']}\n")
    
    # Buscar novamente (com cache)
    print("2️⃣ Buscando user 1 novamente (cache):")
    response = handler.handle_get_user(1)
    print(f"   Resultado: {response['data']['name']}\n")
    
    # Listar usuários
    print("3️⃣ Listando usuários:")
    response = handler.handle_list_users()
    print(f"   Total: {response['count']}\n")
    
    # Criar usuário
    print("4️⃣ Criando novo usuário:")
    response = handler.handle_create_user("David Costa", "david@example.com", 31)
    print(f"   Novo user: {response['data']['name']}\n")
    
    # ========================================================================
    # MOSTRAR PROBLEMAS INTERNOS
    # ========================================================================
    
    print("\nDIAGNÓSTICO: Problemas Internos")
    print("-" * 80 + "\n")
    
    diag = handler.get_diagnostics()
    
    print("❌ Cache Stats exposto (acoplamento!):")
    print(f"   {diag['cache_stats']}\n")
    
    print("❌ Logs internos exposto (acoplamento!):")
    for log in diag['logs'][-5:]:  # Últimos 5 logs
        print(f"   {log}")
    print()
    
    # ========================================================================
    # COMPARAÇÃO FINAL
    # ========================================================================
    
    print("\n" + "="*80)
    print("🔴 PROBLEMAS DO ALTO ACOPLAMENTO")
    print("="*80 + "\n")
    
    print("❌ PROBLEMA 1: Difícil de Instanciar")
    print("   - Você não controla as dependências")
    print("   - Criadas automaticamente (hardcoded)")
    print("   - Impossível customizar\n")
    
    print("❌ PROBLEMA 2: Impossível Testar")
    print("   - Não pode usar mocks")
    print("   - Precisa de tudo para rodar")
    print("   - Testes ficam lentos e frágeis\n")
    
    print("❌ PROBLEMA 3: Impossível Reutilizar")
    print("   - Carrega todas as dependências")
    print("   - Não funciona em outro contexto")
    print("   - Copy-paste leva a duplicação\n")
    
    print("❌ PROBLEMA 4: Frágil para Mudanças")
    print("   - Mudança em uma dep quebra tudo")
    print("   - Efeito cascata")
    print("   - Refatoração é perigosa\n")
    
    print("❌ PROBLEMA 5: Difícil de Entender")
    print("   - Não é claro quais são as dependências")
    print("   - Precisa ler o código para saber")
    print("   - Onboarding de novos devs é difícil\n")
    
    print("❌ PROBLEMA 6: Expõe Detalhes Internos")
    print("   - Cache stats exposto")
    print("   - Logs internos exposto")
    print("   - Viola encapsulamento\n")
    
    print("="*80 + "\n")


def comparacao_estrutural():
    """Mostra a estrutura comparada"""
    
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO ESTRUTURAL: BAIXO vs MÉDIO vs ALTO")
    print("="*80 + "\n")
    
    print("BAIXO ACOPLAMENTO ✅:")
    print("-" * 80)
    print("├─ Logger (0 deps)")
    print("├─ Validator (0 deps)")
    print("├─ Models (0 deps)")
    print("├─ Utils (0 deps)")
    print("└─ Repository (0 deps)")
    print("\n✅ Cada módulo 100% independente")
    print("✅ Total de acoplamentos: 0")
    print("✅ Entropia: ~0 bits\n")
    
    print("\nMÉDIO ACOPLAMENTO 🟡:")
    print("-" * 80)
    print("└─ Cache (0 deps)")
    print("   └─ Database (1 dep: Cache)")
    print("      └─ UserService (1 dep: Database)")
    print("         └─ UserController (1 dep: UserService)")
    print("\n🟡 Hierarquia clara em cadeia")
    print("🟡 Total de acoplamentos: 3")
    print("🟡 Entropia: ~0.8 bits\n")
    
    print("\nALTO ACOPLAMENTO 🔴:")
    print("-" * 80)
    print("└─ UserService (HARDCODED:")
    print("   ├─ Logger()")
    print("   ├─ Cache()")
    print("   └─ Database()")
    print("   │")
    print("   └─ UserHandler (depende de UserService)")
    print("\n🔴 Dependências concentradas")
    print("🔴 Total de acoplamentos: 4+")
    print("🔴 Entropia: ~1.2+ bits")
    print("🔴 Status: ANTI-PADRÃO!\n")


def exemplo_problemas_praticos():
    """Exemplos de problemas práticos"""
    
    print("\n" + "="*80)
    print("🔴 PROBLEMAS PRÁTICOS DO ALTO ACOPLAMENTO")
    print("="*80 + "\n")
    
    print("CENÁRIO 1: Mudar Logger de Console para File")
    print("-" * 80)
    print("\n❌ COM ALTO ACOPLAMENTO:")
    print("""
    class UserService:
        def __init__(self):
            self.logger = Logger("UserService")  # Hardcoded!
            # ... outros deps
    
    Problema:
    - Precisa editar UserService
    - Afeta todos que usam UserService
    - Risco de quebrar testes
    - Refatoração cara
    """)
    
    print("\n✅ COM MÉDIO ACOPLAMENTO:")
    print("""
    class UserService:
        def __init__(self, logger):
            self.logger = logger  # Injetado!
    
    # Usar com Logger de console
    service = UserService(ConsoleLogger())
    
    # Usar com Logger de arquivo
    service = UserService(FileLogger())
    
    Vantagens:
    - Sem mudanças em UserService
    - Fácil trocar logger
    - Testes usam MockLogger
    """)
    
    print("\nCENÁRIO 2: Adicionar segundo Cache")
    print("-" * 80)
    print("\n❌ COM ALTO ACOPLAMENTO:")
    print("""
    class UserService:
        def __init__(self):
            self.cache = Cache()  # Um cache hardcoded
            # Impossível usar dois!
    
    Problema:
    - Precisa editar UserService
    - Pode quebrar existentes
    - Difícil de refatorar
    """)
    
    print("\n✅ COM MÉDIO ACOPLAMENTO:")
    print("""
    class UserService:
        def __init__(self, cache):
            self.cache = cache  # Qualquer cache!
    
    cache1 = Cache()
    cache2 = Cache()
    
    service1 = UserService(cache1)
    service2 = UserService(cache2)
    
    # Ou compartilhar
    service3 = UserService(cache1)
    """)
    
    print("\nCENÁRIO 3: Testar UserService")
    print("-" * 80)
    print("\n❌ COM ALTO ACOPLAMENTO:")
    print("""
    def test_get_user():
        service = UserService()  # Cria Logger, Cache, Database reais
        # Problema: Teste é lento, frágil, acoplado à implementação
        
        # Não pode fazer:
        # - Logger escreve em arquivo
        # - Cache usa memória (poluição entre testes)
        # - Database acessa banco real
    """)
    
    print("\n✅ COM MÉDIO ACOPLAMENTO:")
    print("""
    def test_get_user():
        class MockDB:
            def get_user(self, id):
                return {'id': id, 'name': 'Mock User'}
        
        service = UserService(MockDB())  # Usa mock!
        
        Vantagens:
        - Teste é rápido
        - Isolado de Logger, Cache, Database
        - Fácil debugar
    """)


if __name__ == "__main__":
    # Executar demonstração principal
    main()
    
    # Mostrar comparação estrutural
    comparacao_estrutural()
    
    # Mostrar problemas práticos
    exemplo_problemas_praticos()
    
    print("\n" + "="*80)
    print("🎓 CONCLUSÃO: O QUE APRENDEMOS")
    print("="*80)
    print("""
    ALTO ACOPLAMENTO = ANTI-PADRÃO ❌
    ═══════════════════════════════════════════════════════════════════════════
    
    Nunca use quando puder evitar!
    
    Problemas:
    ✗ Difícil de testar
    ✗ Difícil de reutilizar
    ✗ Difícil de manter
    ✗ Difícil de estender
    ✗ Frágil para mudanças
    ✗ Impossível customizar
    
    Solução:
    ✅ Use BAIXO ACOPLAMENTO para máxima flexibilidade
    ✅ Use MÉDIO ACOPLAMENTO para estrutura clara
    ✅ EVITE ALTO ACOPLAMENTO
    
    Regra de Ouro:
    "Programe para interfaces, não para implementações"
    "Injete dependências, não crie hardcoded"
    "Faça seus módulos focados e independentes"
    
    """)
    print("="*80 + "\n")
