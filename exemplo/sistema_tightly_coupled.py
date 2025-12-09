#!/usr/bin/env python3
"""
🔴 SISTEMA TIGHTLY COUPLED (ORIGINAL)
Figura 1: Cada subsistema se comunica diretamente com os outros
Status: ACOPLAMENTO ALTO (direto entre subsistemas)

Estrutura:
    SubsistemaA ↔ SubsistemaB
         ↕              ↕
    SubsistemaC ←→ SubsistemaB
    
Total de acoplamentos diretos: 6 (A-B, A-C, B-C, e vice-versa)
"""

import json
from typing import Dict, Any

# ============================================================================
# SUBSISTEMA A - Acoplado diretamente a B e C
# ============================================================================

class SubsistemaA:
    """
    ❌ ALTO ACOPLAMENTO: Conhece e depende diretamente de B e C
    """
    
    def __init__(self):
        self.nome = "Subsistema A"
        self.dados = {
            "usuarios": [
                {"id": 1, "nome": "Alice"},
                {"id": 2, "nome": "Bob"}
            ]
        }
        # 🔴 ACOPLAMENTO: Importações diretas
        self.subsistema_b = None
        self.subsistema_c = None
    
    def conectar_subsistemas(self, b, c):
        """Conecta diretamente aos outros subsistemas"""
        self.subsistema_b = b
        self.subsistema_c = c
        print(f"[{self.nome}] Conectado diretamente a B e C ❌")
    
    def obter_dados_de_b(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de B diretamente
        Se B mudar, A quebra
        """
        if not self.subsistema_b:
            return None
        dados_b = self.subsistema_b.get_dados()
        print(f"[{self.nome}] Chamou B diretamente: {dados_b}")
        return dados_b
    
    def obter_dados_de_c(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de C diretamente
        Se C mudar, A quebra
        """
        if not self.subsistema_c:
            return None
        dados_c = self.subsistema_c.get_dados()
        print(f"[{self.nome}] Chamou C diretamente: {dados_c}")
        return dados_c
    
    def processar_com_dados_externos(self):
        """Processa usando dados obtidos diretamente de B e C"""
        dados_b = self.obter_dados_de_b()
        dados_c = self.obter_dados_de_c()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados,
            "dados_de_b": dados_b,
            "dados_de_c": dados_c
        }
        return resultado
    
    def get_dados(self):
        return self.dados


# ============================================================================
# SUBSISTEMA B - Acoplado diretamente a A e C
# ============================================================================

class SubsistemaB:
    """
    ❌ ALTO ACOPLAMENTO: Conhece e depende diretamente de A e C
    """
    
    def __init__(self):
        self.nome = "Subsistema B"
        self.dados = {
            "pedidos": [
                {"id": 101, "cliente": "Alice", "valor": 150.00},
                {"id": 102, "cliente": "Bob", "valor": 200.00}
            ]
        }
        # 🔴 ACOPLAMENTO: Importações diretas
        self.subsistema_a = None
        self.subsistema_c = None
    
    def conectar_subsistemas(self, a, c):
        """Conecta diretamente aos outros subsistemas"""
        self.subsistema_a = a
        self.subsistema_c = c
        print(f"[{self.nome}] Conectado diretamente a A e C ❌")
    
    def obter_dados_de_a(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de A diretamente
        """
        if not self.subsistema_a:
            return None
        dados_a = self.subsistema_a.get_dados()
        print(f"[{self.nome}] Chamou A diretamente: {dados_a}")
        return dados_a
    
    def obter_dados_de_c(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de C diretamente
        """
        if not self.subsistema_c:
            return None
        dados_c = self.subsistema_c.get_dados()
        print(f"[{self.nome}] Chamou C diretamente: {dados_c}")
        return dados_c
    
    def processar_com_dados_externos(self):
        """Processa usando dados obtidos diretamente de A e C"""
        dados_a = self.obter_dados_de_a()
        dados_c = self.obter_dados_de_c()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados,
            "dados_de_a": dados_a,
            "dados_de_c": dados_c
        }
        return resultado
    
    def get_dados(self):
        return self.dados


# ============================================================================
# SUBSISTEMA C - Acoplado diretamente a A e B
# ============================================================================

class SubsistemaC:
    """
    ❌ ALTO ACOPLAMENTO: Conhece e depende diretamente de A e B
    """
    
    def __init__(self):
        self.nome = "Subsistema C"
        self.dados = {
            "inventario": [
                {"produto": "Notebook", "quantidade": 10},
                {"produto": "Mouse", "quantidade": 50}
            ]
        }
        # 🔴 ACOPLAMENTO: Importações diretas
        self.subsistema_a = None
        self.subsistema_b = None
    
    def conectar_subsistemas(self, a, b):
        """Conecta diretamente aos outros subsistemas"""
        self.subsistema_a = a
        self.subsistema_b = b
        print(f"[{self.nome}] Conectado diretamente a A e B ❌")
    
    def obter_dados_de_a(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de A diretamente
        """
        if not self.subsistema_a:
            return None
        dados_a = self.subsistema_a.get_dados()
        print(f"[{self.nome}] Chamou A diretamente: {dados_a}")
        return dados_a
    
    def obter_dados_de_b(self):
        """
        🔴 ACOPLAMENTO DIRETO: Chama método de B diretamente
        """
        if not self.subsistema_b:
            return None
        dados_b = self.subsistema_b.get_dados()
        print(f"[{self.nome}] Chamou B diretamente: {dados_b}")
        return dados_b
    
    def processar_com_dados_externos(self):
        """Processa usando dados obtidos diretamente de A e B"""
        dados_a = self.obter_dados_de_a()
        dados_b = self.obter_dados_de_b()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados,
            "dados_de_a": dados_a,
            "dados_de_b": dados_b
        }
        return resultado
    
    def get_dados(self):
        return self.dados


# ============================================================================
# MAIN: Demonstração do Sistema Tightly Coupled
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🔴 SISTEMA ORIGINAL - TIGHTLY COUPLED (Figura 1)")
    print("="*80)
    print("\nEstrutura:")
    print("    SubsistemaA ↔ SubsistemaB")
    print("         ↕            ↕")
    print("    SubsistemaC ←→ SubsistemaB")
    print("\nTotal de acoplamentos diretos: 6 (A-B, A-C, B-C bidirecionais)")
    print("\n" + "="*80 + "\n")
    
    # Criar subsistemas
    a = SubsistemaA()
    b = SubsistemaB()
    c = SubsistemaC()
    
    # Conectar tudo diretamente
    print("📌 CONECTANDO SUBSISTEMAS:\n")
    a.conectar_subsistemas(b, c)
    b.conectar_subsistemas(a, c)
    c.conectar_subsistemas(a, b)
    
    # Executar operações
    print("\n" + "="*80)
    print("🔄 EXECUTANDO OPERAÇÕES (com chamadas diretas)")
    print("="*80 + "\n")
    
    print("1️⃣ Subsistema A processando com dados de B e C:")
    print("-" * 80)
    resultado_a = a.processar_com_dados_externos()
    print(f"Resultado: {json.dumps(resultado_a, indent=2, ensure_ascii=False)}\n")
    
    print("2️⃣ Subsistema B processando com dados de A e C:")
    print("-" * 80)
    resultado_b = b.processar_com_dados_externos()
    print(f"Resultado: {json.dumps(resultado_b, indent=2, ensure_ascii=False)}\n")
    
    print("3️⃣ Subsistema C processando com dados de A e B:")
    print("-" * 80)
    resultado_c = c.processar_com_dados_externos()
    print(f"Resultado: {json.dumps(resultado_c, indent=2, ensure_ascii=False)}\n")
    
    # Análise do acoplamento
    print("\n" + "="*80)
    print("❌ PROBLEMAS DO SISTEMA TIGHTLY COUPLED")
    print("="*80)
    print("""
    PROBLEMA 1: Acoplamento Direto
    └─ Cada subsistema conhece a interface dos outros
    └─ Mudança em um afeta todos os outros
    └─ Risco alto de quebra em cascata
    
    PROBLEMA 2: Difícil de Testar
    └─ Para testar A, precisa de B e C prontos
    └─ Não pode usar mocks facilmente
    └─ Testes são lentos e frágeis
    
    PROBLEMA 3: Difícil de Estender
    └─ Adicionar novo subsistema D requer mudança em A, B, C
    └─ Cada subsistema precisa conhecer todos os outros
    
    PROBLEMA 4: Compartilhamento de Dados Redundante
    └─ Cada subsistema possui cópia dos mesmos dados
    └─ Inconsistência entre cópias
    └─ Sincronização manual e complexa
    
    PROBLEMA 5: Alto Acoplamento de Dados
    └─ 6 acoplamentos diretos (3 subsistemas × 2 direções)
    └─ Mudança em formato de dados quebra múltiplos subsistemas
    └─ Difícil manutenção
    """)
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
