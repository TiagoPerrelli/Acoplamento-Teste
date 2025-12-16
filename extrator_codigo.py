#!/usr/bin/env python3
"""
Módulo de extração de funções e variáveis do código Python
"""

import ast
from pathlib import Path
from collections import defaultdict


class ExtratorCodigo:
    """Extrai funções, variáveis e dependências de um projeto Python"""

    # Built-ins e keywords do Python que devem ser ignorados
    BUILT_INS = {
        # Funções built-in comuns
        'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 
        'tuple', 'type', 'isinstance', 'issubclass', 'hasattr', 'getattr', 'setattr',
        'input', 'open', 'file', 'iter', 'next', 'enumerate', 'zip', 'map', 'filter',
        'sum', 'min', 'max', 'abs', 'round', 'pow', 'divmod', 'all', 'any', 'sorted',
        'reversed', 'chr', 'ord', 'hex', 'oct', 'bin', 'format', 'repr', 'eval', 'exec',
        'compile', 'globals', 'locals', 'vars', 'dir', 'help', 'id', 'hash', 'object',
        'staticmethod', 'classmethod', 'property', 'super', 'callable',

        # Exceções comuns
        'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError', 'AttributeError',
        'RuntimeError', 'StopIteration', 'GeneratorExit', 'KeyboardInterrupt',

        # Keywords (já filtrados pelo AST mas por garantia)
        'True', 'False', 'None', 'and', 'or', 'not', 'if', 'else', 'elif', 'while',
        'for', 'in', 'is', 'return', 'break', 'continue', 'pass', 'def', 'class',
        'try', 'except', 'finally', 'raise', 'with', 'as', 'import', 'from',
        'lambda', 'yield', 'assert', 'del', 'global', 'nonlocal',

        # Outros comuns
        'self', 'cls', '__name__', '__main__', '__init__', '__str__', '__repr__',
    }

    def __init__(self, pasta_projeto):
        self.pasta_projeto = Path(pasta_projeto)
        self.funcoes = {}
        self.chamadas = defaultdict(set)
        self.variaveis = {}
        self.var_dependencies = defaultdict(set)

        self._encontrar_funcoes()
        self._analisar_chamadas()
        self._extrair_variaveis()
        self._analisar_dependencias_variaveis()

    def _encontrar_funcoes(self):
        """Encontra todas as funções em arquivos Python"""
        for arquivo in self.pasta_projeto.rglob("*.py"):
            if "__pycache__" in str(arquivo):
                continue

            try:
                with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()

                try:
                    tree = ast.parse(conteudo)
                except:
                    continue

                relativo = str(arquivo.relative_to(self.pasta_projeto)).replace("\\", "/")
                modulo = relativo.replace(".py", "").replace("/", ".")

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        nome_qualificado = f"{modulo}.{node.name}"
                        self.funcoes[nome_qualificado] = {
                            "arquivo": relativo,
                            "linha": node.lineno,
                            "nome": node.name,
                            "node": node
                        }

            except:
                pass

        print(f"📂 Encontradas {len(self.funcoes)} funções")

    def _analisar_chamadas(self):
        """Analisa chamadas de funções"""
        for nome_func, info_func in self.funcoes.items():
            node_func = info_func["node"]

            for node in ast.walk(node_func):
                if isinstance(node, ast.Call):
                    funcao_chamada = self._extrair_nome_chamada(node)

                    if funcao_chamada:
                        for nome_alvo in self.funcoes.keys():
                            if funcao_chamada in nome_alvo or nome_alvo.endswith(funcao_chamada):
                                if nome_alvo != nome_func:
                                    self.chamadas[nome_func].add(nome_alvo)

    def _extrair_nome_chamada(self, node_call):
        if isinstance(node_call.func, ast.Name):
            return node_call.func.id
        elif isinstance(node_call.func, ast.Attribute):
            return node_call.func.attr
        return None

    def _eh_variavel_valida(self, nome_var):
        """Verifica se o nome é uma variável válida (não built-in, não privada demais)"""
        if nome_var in self.BUILT_INS:
            return False
        if nome_var.startswith('__') and nome_var.endswith('__'):  # __dunder__
            return False
        if len(nome_var) <= 1:  # Variáveis de 1 letra geralmente são loops (i, j, x)
            return False
        return True

    def _extrair_variaveis(self):
        """Extrai todas as variáveis e conta TODAS as ocorrências (Xi = total de usos)"""
        var_freq = defaultdict(int)  # Conta TODAS as ocorrências
        var_funcoes = defaultdict(set)

        for nome_func, info_func in self.funcoes.items():
            node_func = info_func["node"]

            # Contar TODAS as ocorrências de cada variável
            for node in ast.walk(node_func):
                # Contar uso de variáveis (ast.Name cobre atribuições, leituras, etc.)
                if isinstance(node, ast.Name):
                    var_nome = node.id

                    # Filtrar built-ins e variáveis inválidas
                    if not self._eh_variavel_valida(var_nome):
                        continue

                    var_nome_completo = f"{nome_func}::{var_nome}"
                    var_freq[var_nome_completo] += 1  # Incrementa a cada uso
                    var_funcoes[var_nome_completo].add(nome_func)

        # Criar dicionário de variáveis com frequência correta
        for var_nome, freq in var_freq.items():
            self.variaveis[var_nome] = {
                "nome": var_nome.split("::")[-1],
                "funcao": var_nome.split("::")[0],
                "frequencia": freq,  # Xi = total de usos
                "num_funcoes": len(var_funcoes[var_nome])
            }

        print(f"📊 Encontradas {len(self.variaveis)} variáveis (filtradas)")

        # Debug: mostrar algumas variáveis e suas frequências
        if self.variaveis:
            print(f"\n🔍 Amostra de variáveis encontradas:")
            for i, (var_nome, info) in enumerate(list(self.variaveis.items())[:5]):
                var_simples = var_nome.split("::")[-1]
                print(f"   {var_simples}: Xi = {info['frequencia']} usos")

    def _analisar_dependencias_variaveis(self):
        """Analisa dependências entre variáveis (a = b + c significa que 'a' depende de 'b' e 'c')"""
        for nome_func, info_func in self.funcoes.items():
            node_func = info_func["node"]

            # Para cada atribuição, ver quais variáveis são usadas no lado direito
            for node in ast.walk(node_func):
                if isinstance(node, ast.Assign):
                    # Variável sendo atribuída (lado esquerdo)
                    vars_atribuidas = set()
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if self._eh_variavel_valida(target.id):
                                var_completa = f"{nome_func}::{target.id}"
                                vars_atribuidas.add(var_completa)

                    # Variáveis usadas na expressão (lado direito)
                    vars_usadas = set()
                    for subnode in ast.walk(node.value):
                        if isinstance(subnode, ast.Name):
                            if self._eh_variavel_valida(subnode.id):
                                var_usada = f"{nome_func}::{subnode.id}"
                                if var_usada in self.variaveis:
                                    vars_usadas.add(var_usada)

                    # Criar dependências: variável atribuída depende das usadas
                    for var_atribuida in vars_atribuidas:
                        if var_atribuida in self.variaveis:
                            for var_usada in vars_usadas:
                                if var_atribuida != var_usada:
                                    self.var_dependencies[var_atribuida].add(var_usada)
