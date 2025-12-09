#!/usr/bin/env python3
"""
✅ SISTEMA LOOSELY COUPLED COM DATA WAREHOUSE (MELHORADO)
Figura 2: Subsistemas se comunicam APENAS via Data Warehouse
Status: ACOPLAMENTO BAIXO (desacoplado via intermediário)

Estrutura:
    SubsistemaA
         ↓
    Data Warehouse ← Ponto central único
         ↑
    SubsistemaB    SubsistemaC
    
Total de acoplamentos: Reduzidos significativamente
Cada subsistema só conhece o Data Warehouse, não os outros
"""

import json
from typing import Dict, Any, List
from datetime import datetime

# ============================================================================
# DATA WAREHOUSE - Intermediário Central
# ============================================================================

class DataWarehouse:
    """
    ✅ PONTO CENTRAL: Todos os subsistemas se comunicam através disso
    Desacopla os subsistemas entre si
    """
    
    def __init__(self):
        self.nome = "Data Warehouse"
        # Armazenar dados consolidados de todos os subsistemas
        self.dados_consolidados = {
            "usuarios": [],
            "pedidos": [],
            "inventario": []
        }
        self.historico_alteracoes = []
        
        print(f"[{self.nome}] Iniciado como ponto central de comunicação ✅")
    
    def registrar_dados_usuario(self, dados):
        """Subsistema A envia dados de usuários para o warehouse"""
        self.dados_consolidados["usuarios"] = dados
        self._registrar_alteracao("usuarios", dados)
        print(f"[{self.nome}] Dados de usuários recebidos e armazenados ✅")
    
    def registrar_dados_pedidos(self, dados):
        """Subsistema B envia dados de pedidos para o warehouse"""
        self.dados_consolidados["pedidos"] = dados
        self._registrar_alteracao("pedidos", dados)
        print(f"[{self.nome}] Dados de pedidos recebidos e armazenados ✅")
    
    def registrar_dados_inventario(self, dados):
        """Subsistema C envia dados de inventário para o warehouse"""
        self.dados_consolidados["inventario"] = dados
        self._registrar_alteracao("inventario", dados)
        print(f"[{self.nome}] Dados de inventário recebidos e armazenados ✅")
    
    def obter_dados_usuarios(self):
        """Retorna dados de usuários para qualquer subsistema"""
        return self.dados_consolidados["usuarios"]
    
    def obter_dados_pedidos(self):
        """Retorna dados de pedidos para qualquer subsistema"""
        return self.dados_consolidados["pedidos"]
    
    def obter_dados_inventario(self):
        """Retorna dados de inventário para qualquer subsistema"""
        return self.dados_consolidados["inventario"]
    
    def obter_view_integrada(self):
        """Retorna uma view consolidada de todos os dados"""
        return self.dados_consolidados.copy()
    
    def _registrar_alteracao(self, tipo, dados):
        """Log de auditoria"""
        self.historico_alteracoes.append({
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "dados_count": len(dados) if isinstance(dados, list) else 1
        })
    
    def obter_historico(self):
        """Retorna histórico de alterações"""
        return self.historico_alteracoes


# ============================================================================
# SUBSISTEMA A - Apenas comunica com Data Warehouse
# ============================================================================

class SubsistemaA:
    """
    ✅ BAIXO ACOPLAMENTO: Apenas conhece o Data Warehouse
    Não conhece B ou C
    """
    
    def __init__(self, warehouse: DataWarehouse):
        self.nome = "Subsistema A"
        self.warehouse = warehouse  # ✅ Única dependência
        self.dados_locais = {
            "usuarios": [
                {"id": 1, "nome": "Alice"},
                {"id": 2, "nome": "Bob"}
            ]
        }
        print(f"[{self.nome}] Conectado ao Data Warehouse ✅ (não conhece B ou C)")
    
    def enviar_dados_para_warehouse(self):
        """
        ✅ DESACOPLAMENTO: Apenas envia para warehouse
        Não sabe para onde os dados irão
        """
        self.warehouse.registrar_dados_usuario(self.dados_locais["usuarios"])
        print(f"[{self.nome}] Dados enviados para warehouse ✅\n")
    
    def obter_dados_de_outros_subsistemas(self):
        """
        ✅ DESACOPLAMENTO: Obtém dados via warehouse
        Não chama B ou C diretamente
        """
        dados_pedidos = self.warehouse.obter_dados_pedidos()
        dados_inventario = self.warehouse.obter_dados_inventario()
        
        print(f"[{self.nome}] Obteve dados de pedidos via warehouse: {dados_pedidos}")
        print(f"[{self.nome}] Obteve dados de inventário via warehouse: {dados_inventario}\n")
        
        return {
            "pedidos": dados_pedidos,
            "inventario": dados_inventario
        }
    
    def processar_com_dados_warehouse(self):
        """Processa usando dados obtidos do warehouse"""
        view_integrada = self.warehouse.obter_view_integrada()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados_locais,
            "dados_warehouse": view_integrada
        }
        return resultado
    
    def get_dados(self):
        return self.dados_locais


# ============================================================================
# SUBSISTEMA B - Apenas comunica com Data Warehouse
# ============================================================================

class SubsistemaB:
    """
    ✅ BAIXO ACOPLAMENTO: Apenas conhece o Data Warehouse
    Não conhece A ou C
    """
    
    def __init__(self, warehouse: DataWarehouse):
        self.nome = "Subsistema B"
        self.warehouse = warehouse  # ✅ Única dependência
        self.dados_locais = {
            "pedidos": [
                {"id": 101, "cliente": "Alice", "valor": 150.00},
                {"id": 102, "cliente": "Bob", "valor": 200.00}
            ]
        }
        print(f"[{self.nome}] Conectado ao Data Warehouse ✅ (não conhece A ou C)")
    
    def enviar_dados_para_warehouse(self):
        """
        ✅ DESACOPLAMENTO: Apenas envia para warehouse
        Não sabe para onde os dados irão
        """
        self.warehouse.registrar_dados_pedidos(self.dados_locais["pedidos"])
        print(f"[{self.nome}] Dados enviados para warehouse ✅\n")
    
    def obter_dados_de_outros_subsistemas(self):
        """
        ✅ DESACOPLAMENTO: Obtém dados via warehouse
        Não chama A ou C diretamente
        """
        dados_usuarios = self.warehouse.obter_dados_usuarios()
        dados_inventario = self.warehouse.obter_dados_inventario()
        
        print(f"[{self.nome}] Obteve dados de usuários via warehouse: {dados_usuarios}")
        print(f"[{self.nome}] Obteve dados de inventário via warehouse: {dados_inventario}\n")
        
        return {
            "usuarios": dados_usuarios,
            "inventario": dados_inventario
        }
    
    def processar_com_dados_warehouse(self):
        """Processa usando dados obtidos do warehouse"""
        view_integrada = self.warehouse.obter_view_integrada()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados_locais,
            "dados_warehouse": view_integrada
        }
        return resultado
    
    def get_dados(self):
        return self.dados_locais


# ============================================================================
# SUBSISTEMA C - Apenas comunica com Data Warehouse
# ============================================================================

class SubsistemaC:
    """
    ✅ BAIXO ACOPLAMENTO: Apenas conhece o Data Warehouse
    Não conhece A ou B
    """
    
    def __init__(self, warehouse: DataWarehouse):
        self.nome = "Subsistema C"
        self.warehouse = warehouse  # ✅ Única dependência
        self.dados_locais = {
            "inventario": [
                {"produto": "Notebook", "quantidade": 10},
                {"produto": "Mouse", "quantidade": 50}
            ]
        }
        print(f"[{self.nome}] Conectado ao Data Warehouse ✅ (não conhece A ou B)")
    
    def enviar_dados_para_warehouse(self):
        """
        ✅ DESACOPLAMENTO: Apenas envia para warehouse
        Não sabe para onde os dados irão
        """
        self.warehouse.registrar_dados_inventario(self.dados_locais["inventario"])
        print(f"[{self.nome}] Dados enviados para warehouse ✅\n")
    
    def obter_dados_de_outros_subsistemas(self):
        """
        ✅ DESACOPLAMENTO: Obtém dados via warehouse
        Não chama A ou B diretamente
        """
        dados_usuarios = self.warehouse.obter_dados_usuarios()
        dados_pedidos = self.warehouse.obter_dados_pedidos()
        
        print(f"[{self.nome}] Obteve dados de usuários via warehouse: {dados_usuarios}")
        print(f"[{self.nome}] Obteve dados de pedidos via warehouse: {dados_pedidos}\n")
        
        return {
            "usuarios": dados_usuarios,
            "pedidos": dados_pedidos
        }
    
    def processar_com_dados_warehouse(self):
        """Processa usando dados obtidos do warehouse"""
        view_integrada = self.warehouse.obter_view_integrada()
        
        resultado = {
            "origem": self.nome,
            "dados_proprios": self.dados_locais,
            "dados_warehouse": view_integrada
        }
        return resultado
    
    def get_dados(self):
        return self.dados_locais


# ============================================================================
# MAIN: Demonstração do Sistema com Data Warehouse
# ============================================================================

def main():
    print("\n" + "="*80)
    print("✅ SISTEMA MELHORADO - LOOSELY COUPLED COM DATA WAREHOUSE (Figura 2)")
    print("="*80)
    print("\nEstrutura:")
    print("    SubsistemaA")
    print("         ↓")
    print("    Data Warehouse ← Ponto central único")
    print("         ↑")
    print("    SubsistemaB    SubsistemaC")
    print("\nAcoplamento reduzido significativamente!")
    print("Cada subsistema só conhece o Data Warehouse")
    print("\n" + "="*80 + "\n")
    
    # Criar Data Warehouse
    warehouse = DataWarehouse()
    print()
    
    # Criar subsistemas (todos com referência apenas ao warehouse)
    print("📌 CRIANDO SUBSISTEMAS:\n")
    a = SubsistemaA(warehouse)
    b = SubsistemaB(warehouse)
    c = SubsistemaC(warehouse)
    
    # Fase 1: Enviar dados para warehouse
    print("\n" + "="*80)
    print("📤 FASE 1: ENVIANDO DADOS PARA O WAREHOUSE")
    print("="*80 + "\n")
    
    a.enviar_dados_para_warehouse()
    b.enviar_dados_para_warehouse()
    c.enviar_dados_para_warehouse()
    
    # Fase 2: Subsistemas obtêm dados via warehouse
    print("="*80)
    print("📥 FASE 2: OBTENDO DADOS VIA WAREHOUSE")
    print("="*80 + "\n")
    
    print("Subsistema A obtendo dados de B e C (via warehouse):")
    print("-" * 80)
    dados_a = a.obter_dados_de_outros_subsistemas()
    
    print("Subsistema B obtendo dados de A e C (via warehouse):")
    print("-" * 80)
    dados_b = b.obter_dados_de_outros_subsistemas()
    
    print("Subsistema C obtendo dados de A e B (via warehouse):")
    print("-" * 80)
    dados_c = c.obter_dados_de_outros_subsistemas()
    
    # Fase 3: Processamento
    print("\n" + "="*80)
    print("🔄 FASE 3: PROCESSAMENTO COM DADOS DO WAREHOUSE")
    print("="*80 + "\n")
    
    print("1️⃣ Subsistema A processando com dados do warehouse:")
    print("-" * 80)
    resultado_a = a.processar_com_dados_warehouse()
    print(f"Resultado: {json.dumps(resultado_a, indent=2, ensure_ascii=False)}\n")
    
    print("2️⃣ Subsistema B processando com dados do warehouse:")
    print("-" * 80)
    resultado_b = b.processar_com_dados_warehouse()
    print(f"Resultado: {json.dumps(resultado_b, indent=2, ensure_ascii=False)}\n")
    
    print("3️⃣ Subsistema C processando com dados do warehouse:")
    print("-" * 80)
    resultado_c = c.processar_com_dados_warehouse()
    print(f"Resultado: {json.dumps(resultado_c, indent=2, ensure_ascii=False)}\n")
    
    # Análise do desacoplamento
    print("\n" + "="*80)
    print("✅ BENEFÍCIOS DO SISTEMA LOOSELY COUPLED COM DATA WAREHOUSE")
    print("="*80)
    print("""
    BENEFÍCIO 1: Desacoplamento Completo
    └─ Cada subsistema apenas conhece o Data Warehouse
    └─ A não conhece B ou C (e vice-versa)
    └─ Mudança em um não afeta os outros diretamente
    
    BENEFÍCIO 2: Fácil de Testar
    └─ Para testar A, pode mockar apenas o warehouse
    └─ Não precisa de B e C prontos
    └─ Testes são rápidos e isolados
    
    BENEFÍCIO 3: Fácil de Estender
    └─ Adicionar novo subsistema D é trivial
    └─ D se conecta ao warehouse, sem afetar A, B, C
    └─ Escalabilidade natural
    
    BENEFÍCIO 4: Fonte Única da Verdade
    └─ Todos os dados estão centralizados no warehouse
    └─ Uma versão única de cada dado
    └─ Sem inconsistências entre cópias
    
    BENEFÍCIO 5: Fluxo de Dados Claro
    └─ Dados fluem: Subsistema → Warehouse → Subsistemas
    └─ Rastreamento fácil de onde vêm os dados
    └─ Auditoria simplificada
    
    BENEFÍCIO 6: Redução do Acoplamento de Dados
    └─ De 6 acoplamentos diretos para 3 (via warehouse)
    └─ Mudança em formato de dados afeta apenas warehouse
    └─ Subsistemas adaptam-se via transformação
    """)
    
    # Mostrar histórico
    print("\n" + "="*80)
    print("📋 HISTÓRICO DE ALTERAÇÕES NO WAREHOUSE")
    print("="*80 + "\n")
    
    historico = warehouse.obter_historico()
    for evento in historico:
        print(f"  {evento['timestamp']} | {evento['tipo']:12} | {evento['dados_count']} item(ns)")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
