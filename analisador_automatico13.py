#!/usr/bin/env python3
"""
📊 ANALISADOR AUTOMÁTICO DE ACOPLAMENTO DE FUNÇÕES
Suporta 2 metodologias:
1. Zhang et al. (2011) - Entropy + Judgment Matrix Models
2. Dou et al. (2023) - VRM Model (Variable Requirement Model)

MODO DE USO:
1. Execute normal (com padrão 0.5):
   python analisador_automatico.py ./seu_projeto

2. Execute com probabilidades personalizadas (modo interativo):
   python analisador_automatico.py ./seu_projeto -p

O sistema:
- Encontra todas as FUNÇÕES em arquivos Python
- Analisa CHAMADAS de funções (dependências)
- Calcula acoplamento usando DUAS metodologias diferentes
- Gera 2 relatórios HTML com resultados comparativos

FLAG -p: Solicita probabilidade de mudança para cada função (Zhang apenas)
"""

import os
import sys
import ast
import math
import numpy as np
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# ============================================================================
# ANALISADOR DE FUNÇÕES E CHAMADAS
# ============================================================================

class AnalisadorFuncoes:
    """Analisa funções Python e suas dependências automaticamente"""
    
    def __init__(self, pasta_projeto):
        self.pasta_projeto = Path(pasta_projeto)
        self.funcoes = {}
        self.chamadas = defaultdict(set)
        
        self._encontrar_funcoes()
        self._analisar_chamadas()
    
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
    
    def obter_matriz_adjacencia(self, funcoes_ordenadas):
        n = len(funcoes_ordenadas)
        matriz = np.zeros((n, n))
        
        indice_map = {f: i for i, f in enumerate(funcoes_ordenadas)}
        
        for origem, destinos in self.chamadas.items():
            if origem in indice_map:
                i = indice_map[origem]
                for destino in destinos:
                    if destino in indice_map:
                        j = indice_map[destino]
                        matriz[i][j] += 1
        
        return matriz


# ============================================================================
# SOLICITAR PROBABILIDADES DO USUÁRIO (APENAS PARA ZHANG)
# ============================================================================

def solicitar_probabilidades(funcoes_ordenadas):
    """Solicita ao usuário as probabilidades de mudança de cada função"""
    print("\n" + "="*70)
    print("📊 DEFINA A PROBABILIDADE DE MUDANÇA DAS FUNÇÕES")
    print("="*70)
    print("\nDigite o índice da função e sua probabilidade (0 a 1), separados por vírgula.")
    print("Exemplo: 1, 0.3  (significa que a função [1] tem probabilidade 0.3)")
    print("Deixe em branco para usar padrão 0.5 para todas as funções.")
    print("\nFunções encontradas:\n")
    
    for idx, funcao in enumerate(funcoes_ordenadas, 1):
        nome_curto = funcao.split('.')[-1]
        arquivo = funcao.split('.')[0]
        print(f"[{idx}] {nome_curto:30} ({arquivo})")
    
    probabilidades = {funcao: 0.5 for funcao in funcoes_ordenadas}
    
    print("\n" + "-"*70)
    print("Digite as probabilidades (ou deixe em branco para padrão 0.5):")
    print("Exemplo de entrada múltipla:")
    print("  1, 0.3")
    print("  2, 0.7")
    print("  5, 0.2")
    print("Digite 'pronto' ou pressione Enter vazio quando terminar.")
    print("-"*70 + "\n")
    
    while True:
        entrada = input(">>> ").strip()
        
        if entrada == "" or entrada.lower() == "pronto":
            break
        
        try:
            partes = entrada.split(',')
            idx = int(partes[0].strip())
            prob = float(partes[1].strip())
            
            if idx < 1 or idx > len(funcoes_ordenadas):
                print(f"❌ Índice inválido! Use valores entre 1 e {len(funcoes_ordenadas)}")
                continue
            
            if prob < 0 or prob > 1:
                print("❌ Probabilidade inválida! Use valores entre 0 e 1")
                continue
            
            funcao = funcoes_ordenadas[idx - 1]
            probabilidades[funcao] = prob
            print(f"✅ [{idx}] = {prob}")
        
        except (ValueError, IndexError):
            print("❌ Formato inválido! Use: número, valor")
            print("Exemplo: 1, 0.3")
    
    print("\n" + "="*70)
    print("📋 PROBABILIDADES DEFINIDAS:")
    print("="*70)
    for idx, funcao in enumerate(funcoes_ordenadas, 1):
        nome_curto = funcao.split('.')[-1]
        prob = probabilidades[funcao]
        print(f"[{idx}] {nome_curto:30} → {prob:.1%}")
    print("="*70 + "\n")
    
    return probabilidades


# ============================================================================
# METODOLOGIA 1: ZHANG ET AL. (2011)
# ============================================================================

class AnalisadorZhang:
    """Implementa metodologia de Zhang et al. (2011)"""
    
    def __init__(self, funcoes, matriz_adjacencia, probabilidades):
        self.funcoes = funcoes
        self.n = len(funcoes)
        self.matriz_adjacencia = matriz_adjacencia
        self.probabilidades = probabilidades
        
        self._contar_acoplas()
        self._calcular_entropy_model()
        self._calcular_judgment_matrix_model()
    
    def _contar_acoplas(self):
        m_temp = self.matriz_adjacencia.copy()
        np.fill_diagonal(m_temp, 0)
        
        self.M = int(np.sum(m_temp) / 2)
        self.M_diretos = int(np.sum(m_temp))
        self.graus = np.sum(self.matriz_adjacencia, axis=1)
    
    def _calcular_entropy_model(self):
        """Calcula Entropy Model usando fórmula corrigida do artigo Zhang et al."""
        H_total = 0.0
        detalhado = []
        
        for i, funcao in enumerate(self.funcoes):
            ni = float(self.graus[i])
            pi = self.probabilidades[funcao]
            
            if ni > 0 and pi > 0 and self.M > 0:
                # Fórmula corrigida: H_c = -Σ (n_i × p_i) / (2M) × log₁₀(n_i / 2M)
                coef = (ni * pi) / (2 * self.M)
                termo = -coef * math.log10(ni / (2 * self.M))
                H_total += termo
            else:
                termo = 0.0
            
            detalhado.append({
                "funcao": funcao,
                "ni": float(ni),
                "pi": float(pi),
                "termo": float(termo)
            })
        
        self.H_entropy = float(H_total)
        self.H_entropy_detalhado = detalhado
        
        # Normalizar H para 0-1
        # H_max teórico = N * p_max * log₁₀(N) (máximo quando todas as funções têm igual probabilidade)
        if self.n > 1:
            H_max = self.n * math.log10(self.n)
            self.H_normalized = min(1.0, self.H_entropy / H_max) if H_max > 0 else 0.0
        else:
            self.H_normalized = 0.0
    
    def classificacao_acoplamento(self):
        """Classifica o nível de acoplamento"""
        if self.H_entropy < 0.33:
            return "✓ Baixo acoplamento"
        elif self.H_entropy < 0.66:
            return "~ Acoplamento moderado"
        else:
            return "✗ Alto acoplamento"
    
    def _calcular_judgment_matrix_model(self):
        A = np.zeros((self.n, self.n))
        
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    A[i][j] = 1.0
                else:
                    n_ij = self.matriz_adjacencia[i][j]
                    
                    if n_ij > 0:
                        soma_i = np.sum(self.matriz_adjacencia[i])
                        if soma_i > 0:
                            A[i][j] = n_ij / soma_i
                        else:
                            A[i][j] = 1.0
                    else:
                        A[i][j] = 1.0
        
        self.matriz_julgamento = A
        
        try:
            eigenvalues, eigenvectors = np.linalg.eig(A)
            lambda_max = np.real(np.max(eigenvalues))
            idx_max = np.argmax(np.real(eigenvalues))
            v_max = np.real(eigenvectors[:, idx_max])
            W = v_max / np.sum(v_max)
            
            self.lambda_max = float(lambda_max)
            self.sorting_vector = W.astype(float)
            
            C_total = 0.0
            for i in range(self.n):
                pi = self.probabilidades[self.funcoes[i]]
                wi = W[i]
                soma_linha = np.sum(A[i])
                C_total += pi * wi * soma_linha
            
            self.C_judgment = float(C_total / self.n)
            
        except Exception as e:
            self.lambda_max = 0.0
            self.sorting_vector = np.ones(self.n) / self.n
            self.C_judgment = 0.0


# ============================================================================
# METODOLOGIA 2: DOU ET AL. (2023) - VRM MODEL
# ============================================================================

class AnalisadorDou:
    """Implementa metodologia de Dou et al. (2023) - VRM Model"""
    
    def __init__(self, funcoes, matriz_adjacencia):
        self.funcoes = funcoes
        self.n = len(funcoes)
        self.matriz_adjacencia = matriz_adjacencia
        
        # Coeficientes baseado em VRM Model
        self.mc_values = {}  # Manual Coefficient
        self.sc_values = {}  # Standard Coefficient
        self.hc_values = {}  # Hierarchical Coefficient
        
        self._calcular_coeficientes()
        self._calcular_acoplamento_vrm()
    
    def _calcular_coeficientes(self):
        """Calcula MC, SC e HC para cada função"""
        
        # Manual Coefficient - preset baseado em análise
        for funcao in self.funcoes:
            self.mc_values[funcao] = 1.0
        
        # Standard Coefficient - Fórmula do artigo Dou et al.
        # SC = X_i + sqrt(Σ(X_i - μ)² / N)
        graus = np.sum(self.matriz_adjacencia, axis=1)
        mu = np.mean(graus)  # Média das ocorrências
        
        for i, funcao in enumerate(self.funcoes):
            Xi = float(graus[i])
            variancia = np.sum((graus - mu) ** 2) / self.n
            desvio_padrao = math.sqrt(variancia)
            # SC = Xi + sqrt(Σ(Xj - μ)² / N)
            self.sc_values[funcao] = Xi + desvio_padrao
        
        # Hierarchical Coefficient - baseado em profundidade na árvore de chamadas
        depths = self._calcular_profundidades()
        for i, funcao in enumerate(self.funcoes):
            depth = depths[i]
            # HC = (depth + complexity) * (1 / 2^depth)
            complexity = graus[i]
            if depth > 0:
                self.hc_values[funcao] = (depth + complexity) * (1.0 / (2.0 ** depth))
            else:
                self.hc_values[funcao] = 1.0
    
    def _calcular_profundidades(self):
        """Calcula profundidade de cada função na árvore de dependências"""
        depths = np.zeros(len(self.funcoes))
        visited = set()
        
        def dfs(idx, depth):
            if idx in visited:
                return
            visited.add(idx)
            depths[idx] = max(depths[idx], depth)
            
            for j in range(len(self.funcoes)):
                if self.matriz_adjacencia[idx][j] > 0:
                    dfs(j, depth + 1)
        
        for i in range(len(self.funcoes)):
            dfs(i, 0)
        
        return depths
    
    def _calcular_acoplamento_vrm(self):
        """Calcula Acoplamento (C) = MC × SC × HC"""
        
        graus = np.sum(self.matriz_adjacencia, axis=1)
        acoplamento_total = 0.0
        sc_total = 0.0
        hc_total = 0.0
        detalhado = []
        
        for i, funcao in enumerate(self.funcoes):
            # Calcula acoplamento: C = MC × SC × HC
            mc = self.mc_values[funcao]
            sc = self.sc_values[funcao]
            hc = self.hc_values[funcao]
            
            acoplamento = mc * sc * hc
            sc_total += sc
            hc_total += hc
            acoplamento_total += acoplamento
            
            detalhado.append({
                "funcao": funcao,
                "mc": float(mc),
                "sc": float(sc),
                "hc": float(hc),
                "acoplamento": float(acoplamento)
            })
        
        # Acoplamento médio (sem normalização)
        self.C_vrm = float(acoplamento_total / self.n) if self.n > 0 else 0.0
        self.HC_vrm = float(hc_total / self.n) if self.n > 0 else 0.0
        self.SC_vrm = float(sc_total / self.n) if self.n > 0 else 0.0
        
        self.detalhado = detalhado
    
    def classificacao_acoplamento(self):
        """Classifica o nível de acoplamento"""
        if self.C_vrm < 2.0:
            return "✓ Baixo acoplamento"
        elif self.C_vrm < 5.0:
            return "~ Acoplamento moderado"
        else:
            return "✗ Alto acoplamento"


# ============================================================================
# GERADOR DE HTML - ZHANG ET AL
# ============================================================================

def gerar_html_zhang(funcoes, analise_zhang):
    """Gera relatório HTML para metodologia Zhang et al. (2011)"""
    
    def format_matriz(funcoes, matriz):
        n = len(funcoes)
        max_show = min(n, 15)
        
        html = '<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:0.75em;">'
        html += '<thead><tr><th style="background:#000;color:#fff;padding:6px;">Função</th>'
        
        for j in range(max_show):
            func_curto = funcoes[j].split('.')[-1][:12]
            html += f'<th style="background:#000;color:#fff;padding:4px;text-align:center;width:40px;">{func_curto}</th>'
        
        if n > max_show:
            html += f'<th style="background:#000;color:#fff;padding:4px;">+{n-max_show}</th>'
        html += '</tr></thead><tbody>'
        
        for i in range(max_show):
            func_curto = funcoes[i].split('.')[-1][:12]
            html += f'<tr><td style="background:#f5f5f5;padding:4px;font-weight:bold;">{func_curto}</td>'
            
            for j in range(max_show):
                valor = int(matriz[i][j])
                if i == j:
                    html += '<td style="text-align:center;padding:4px;border:1px solid #ccc;background:#e0e0e0;">-</td>'
                elif valor > 0:
                    html += f'<td style="text-align:center;padding:4px;border:1px solid #ccc;background:#d3d3d3;font-weight:bold;">{valor}</td>'
                else:
                    html += '<td style="text-align:center;padding:4px;border:1px solid #ccc;background:#fff;">·</td>'
            
            if n > max_show:
                html += '<td style="text-align:center;padding:4px;border:1px solid #ccc;">...</td>'
            html += '</tr>'
        
        if n > max_show:
            html += f'<tr><td colspan="{max_show+2}" style="text-align:center;padding:6px;color:#666;font-size:0.9em;">Mostrando {max_show} de {n} funções</td></tr>'
        
        html += '</tbody></table></div>'
        return html
    
    def format_entropy(detalhado):
        html = ""
        for item in detalhado[:15]:
            func_nome = item['funcao'].split('.')[-1]
            html += f"<tr><td style=\"font-size:0.9em;\">{func_nome}</td><td style=\"text-align:center;\">{int(item['ni'])}</td><td style=\"text-align:center;\">{item['pi']:.1%}</td><td style=\"text-align:center;\">{item['termo']:.4f}</td></tr>"
        
        if len(detalhado) > 15:
            html += f'<tr><td colspan="4" style="text-align:center;padding:4px;color:#666;">... e mais {len(detalhado)-15} funções</td></tr>'
        return html
    
    html_str = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise de Acoplamento - Zhang et al. (2011)</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:Arial,sans-serif;background:#fff;color:#000;padding:20px;line-height:1.6;}}
        .container{{max-width:1400px;margin:0 auto;}}
        header{{border-bottom:2px solid #000;padding:20px 0;margin-bottom:30px;}}
        h1{{font-size:2em;margin-bottom:5px;}}
        .subtitle{{color:#666;font-size:0.95em;margin:3px 0;}}
        h2{{font-size:1.5em;margin:20px 0 15px 0;border-bottom:1px solid #999;padding-bottom:8px;}}
        section{{margin-bottom:30px;}}
        table{{width:100%;border-collapse:collapse;margin:10px 0;background:#fff;}}
        thead tr{{background:#000;color:#fff;}}
        th{{padding:8px;text-align:left;font-weight:bold;border:1px solid #ccc;}}
        td{{padding:6px 8px;border:1px solid #ccc;}}
        tbody tr:nth-child(even){{background:#f9f9f9;}}
        tbody tr:hover{{background:#f0f0f0;}}
        .metric{{display:inline-block;background:#f5f5f5;padding:12px;margin:8px 15px 8px 0;border:1px solid #ccc;}}
        .metric-label{{font-size:0.9em;color:#666;}}
        .metric-value{{font-size:1.4em;font-weight:bold;}}
        .highlight{{background:#f0f0f0;padding:10px;border-left:3px solid #000;margin:10px 0;}}
        .conclusion{{background:#f5f5f5;padding:15px;border:1px solid #999;margin:15px 0;}}
        .note{{font-size:0.85em;color:#666;margin:8px 0;}}
        footer{{border-top:1px solid #999;padding-top:15px;margin-top:30px;color:#666;font-size:0.9em;text-align:center;}}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Análise de Acoplamento: Zhang et al. (2011)</h1>
            <p class="subtitle">Entropy Model + Judgment Matrix Model</p>
            <p class="subtitle">Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </header>
        
        <section>
            <h2>Resumo</h2>
            <table>
                <tr><td><strong>Total de Funções</strong></td><td>{len(funcoes)}</td></tr>
                <tr><td><strong>Chamadas Diretas</strong></td><td>{int(analise_zhang.M_diretos)}</td></tr>
            </table>
        </section>
        
        <section>
            <h2>Resultados Principais</h2>
            <div class="metric">
                <div class="metric-label">Entropy (H):</div>
                <div class="metric-value">{analise_zhang.H_entropy:.4f}</div>
            </div>
        </section>
        
        <section>
            <h2>Matriz de Adjacência</h2>
            <p class="note"><strong>Linhas:</strong> função que chama | <strong>Colunas:</strong> funções chamadas</p>
            {format_matriz(funcoes, analise_zhang.matriz_adjacencia)}
        </section>
        
        <section>
            <h2>Entropy Model - Detalhado</h2>
            <table>
                <thead><tr><th>Função</th><th>Grau (ni)</th><th>Prob. (pi)</th><th>Termo: -(ni×pi/2M)×log₁₀(ni/2M)</th></tr></thead>
                <tbody>{format_entropy(analise_zhang.H_entropy_detalhado)}</tbody>
            </table>
            <div class="highlight">
                <strong>H Total = {analise_zhang.H_entropy:.4f}</strong><br/>
                <p class="note"><strong>Fórmula:</strong> H_c = -Σ (n_i × p_i) / (2M) × log₁₀(n_i / 2M)</p>
            </div>
        </section>
        
        <section>
            <h2>Interpretação</h2>
            <div class="conclusion">
                <p><strong>Entropy (H):</strong> Mede a complexidade da propagação de mudanças entre funções. Quanto maior H, maior o acoplamento.</p>
             </div>
        </section>
        
        <footer>
            <p>Zhang et al. (2011). Quantitative Analysis of System Coupling. IEEE.</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html_str


# ============================================================================
# GERADOR DE HTML - DOU ET AL
# ============================================================================

def gerar_html_dou(funcoes, analise_dou):
    """Gera relatório HTML para metodologia Dou et al. (2023)"""
    
    def format_coeficientes(detalhado):
        html = ""
        for item in detalhado[:15]:
            func_nome = item['funcao'].split('.')[-1]
            html += f"""<tr>
                <td style="font-size:0.9em;">{func_nome}</td>
                <td style="text-align:center;">{item['mc']:.2f}</td>
                <td style="text-align:center;">{item['sc']:.4f}</td>
                <td style="text-align:center;">{item['hc']:.4f}</td>
                <td style="text-align:center;">{item['acoplamento']:.4f}</td>
            </tr>"""
        
        if len(detalhado) > 15:
            html += f'<tr><td colspan="5" style="text-align:center;padding:4px;color:#666;">... e mais {len(detalhado)-15} funções</td></tr>'
        return html
    
    html_str = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise de Acoplamento - Dou et al. (2023)</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:Arial,sans-serif;background:#fff;color:#000;padding:20px;line-height:1.6;}}
        .container{{max-width:1400px;margin:0 auto;}}
        header{{border-bottom:2px solid #000;padding:20px 0;margin-bottom:30px;}}
        h1{{font-size:2em;margin-bottom:5px;}}
        .subtitle{{color:#666;font-size:0.95em;margin:3px 0;}}
        h2{{font-size:1.5em;margin:20px 0 15px 0;border-bottom:1px solid #999;padding-bottom:8px;}}
        section{{margin-bottom:30px;}}
        table{{width:100%;border-collapse:collapse;margin:10px 0;background:#fff;}}
        thead tr{{background:#000;color:#fff;}}
        th{{padding:8px;text-align:left;font-weight:bold;border:1px solid #ccc;font-size:0.9em;}}
        td{{padding:6px 8px;border:1px solid #ccc;}}
        tbody tr:nth-child(even){{background:#f9f9f9;}}
        tbody tr:hover{{background:#f0f0f0;}}
        .metric{{display:inline-block;background:#f5f5f5;padding:12px;margin:8px 15px 8px 0;border:1px solid #ccc;min-width:180px;}}
        .metric-label{{font-size:0.9em;color:#666;}}
        .metric-value{{font-size:1.4em;font-weight:bold;}}
        .highlight{{background:#f0f0f0;padding:10px;border-left:3px solid #000;margin:10px 0;}}
        .conclusion{{background:#f5f5f5;padding:15px;border:1px solid #999;margin:15px 0;}}
        .note{{font-size:0.85em;color:#666;margin:8px 0;}}
        ul{{margin-top:8px;}}
        li{{margin:5px 0;}}
        footer{{border-top:1px solid #999;padding-top:15px;margin-top:30px;color:#666;font-size:0.9em;text-align:center;}}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Análise de Acoplamento: Dou et al. (2023)</h1>
            <p class="subtitle">VRM Model (Variable Requirement Model)</p>
            <p class="subtitle">Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </header>
        
        <section>
            <h2>Resumo</h2>
            <table>
                <tr><td><strong>Total de Funções</strong></td><td>{len(funcoes)}</td></tr>
                <tr><td><strong>Funções Analisadas</strong></td><td>{len(analise_dou.detalhado)}</td></tr>
            </table>
        </section>
        
        <section>
            <h2>Resultados Principais (VRM Model)</h2>
            <div class="metric">
                <div class="metric-label">Acoplamento (C):</div>
                <div class="metric-value">{analise_dou.C_vrm:.4f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Average Hierarchical Coefficient (HC):</div>
                <div class="metric-value">{analise_dou.HC_vrm:.4f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Average Standard Coefficient (SC):</div>
                <div class="metric-value">{analise_dou.SC_vrm:.4f}</div>
            </div>
        </section>
        
        <section>
            <h2>Coeficientes VRM - Análise Detalhada</h2>
            <p class="note"><strong>MC (Manual):</strong> Coeficiente preset | <strong>SC (Standard):</strong> Desvio padrão de requisitos | <strong>HC (Hierarchical):</strong> Baseado em profundidade</p>
            <p class="note"><strong>Acoplamento:</strong> MC × SC × HC</p>
            <table>
                <thead><tr><th>Função</th><th>MC</th><th>SC</th><th>HC</th><th>Acoplamento</th></tr></thead>
                <tbody>{format_coeficientes(analise_dou.detalhado)}</tbody>
            </table>
            <div class="highlight">
                <strong>Acoplamento Médio = {analise_dou.C_vrm:.4f}</strong><br/>
                <p class="note">Baseado em análise de requisitos (sem normalização)</p>
            </div>
        </section>
        
        <section>
            <h2>Metodologia VRM</h2>
            <div class="conclusion">
                <p><strong>MC (Manual Coefficient):</strong> Preset baseado em análise de requisitos (padrão: 1.0).</p>
                <p><strong>SC (Standard Coefficient):</strong> SC = X_i + √(Σ(X_j - μ)² / N)</p>
                <p style="margin-left:20px;font-size:0.9em;">Onde: X_i = ocorrência de variável i, μ = média das ocorrências, N = número de variáveis</p>
                <p><strong>HC (Hierarchical Coefficient):</strong> HC = (profundidade + complexidade) × (1 / 2^profundidade).</p>
                <p><strong>Acoplamento (C):</strong> C = MC × SC × HC (valor sem normalização).</p>
                <p><strong>Interpretação:</strong></p>
                <ul>
                    <li>Valores &lt; 2.0: Baixo acoplamento</li>
                    <li>Valores 2.0 a 5.0: Acoplamento moderado</li>
                    <li>Valores &gt; 5.0: Alto acoplamento</li>
                </ul>
            </div>
        </section>
        
        <footer>
            <p>Dou et al. (2023). A Coupling Analysis Method for Airborne Software Based on Requirement Model.</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html_str


# ============================================================================
# MAIN
# ============================================================================

def mostrar_ajuda():
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║        📊 ANALISADOR DE ACOPLAMENTO - DUAS METODOLOGIAS              ║
║    Zhang et al. (2011) + Dou et al. (2023) [VRM Model]               ║
╚════════════════════════════════════════════════════════════════════════╝

MODO DE USO:

  1. Análise rápida (probabilidade padrão 0.5 para Zhang):
     python analisador_automatico.py ./seu_projeto

  2. Análise com probabilidades personalizadas (apenas Zhang):
     python analisador_automatico.py ./seu_projeto -p

FLAGS:
  -p    Ativa modo interativo (solicita probabilidade para metodologia Zhang)
  -h    Exibe esta mensagem de ajuda

SAÍDA:
  Gera 2 relatórios HTML comparativos:
  - report/analise_automatica_zhang.html
  - report/analise_automatica_dou.html

═══════════════════════════════════════════════════════════════════════════
    """)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        mostrar_ajuda()
        sys.exit(0)
    
    pasta_projeto = sys.argv[1]
    modo_interativo = '-p' in sys.argv
    
    if not os.path.isdir(pasta_projeto):
        print(f"❌ Pasta '{pasta_projeto}' não encontrada!")
        sys.exit(1)
    
    print(f"📊 Analisando funções em: {pasta_projeto}")
    analisador = AnalisadorFuncoes(pasta_projeto)
    
    if not analisador.funcoes:
        print("❌ Nenhuma função encontrada!")
        sys.exit(1)
    
    funcoes_ordenadas = sorted(analisador.funcoes.keys())
    
    if modo_interativo:
        probabilidades = solicitar_probabilidades(funcoes_ordenadas)
    else:
        probabilidades = {funcao: 0.5 for funcao in funcoes_ordenadas}
        print(f"📊 Usando probabilidade padrão 0.5 para todas as {len(funcoes_ordenadas)} funções")
    
    print(f"📊 Analisando chamadas entre {len(funcoes_ordenadas)} funções...")
    matriz = analisador.obter_matriz_adjacencia(funcoes_ordenadas)
    
    # METODOLOGIA 1: ZHANG ET AL.
    print("📊 Calculando métricas Zhang et al. (2011)...")
    analise_zhang = AnalisadorZhang(funcoes_ordenadas, matriz, probabilidades)
    
    # METODOLOGIA 2: DOU ET AL.
    print("📊 Calculando métricas Dou et al. (2023)...")
    analise_dou = AnalisadorDou(funcoes_ordenadas, matriz)
    
    if not os.path.exists("report"):
        os.makedirs("report")
    
    # Gerar relatório Zhang
    html_zhang = gerar_html_zhang(funcoes_ordenadas, analise_zhang)
    with open("report/analise_automatica_zhang.html", "w", encoding="utf-8") as f:
        f.write(html_zhang)
    
    # Gerar relatório Dou
    html_dou = gerar_html_dou(funcoes_ordenadas, analise_dou)
    with open("report/analise_automatica_dou.html", "w", encoding="utf-8") as f:
        f.write(html_dou)
    
    print(f"\n✅ Análise concluída!\n")
    print(f"{'='*70}")
    print(f"📊 RESULTADOS COMPARATIVOS")
    print(f"{'='*70}\n")
    
    print(f"METODOLOGIA 1: Zhang et al. (2011)")
    print(f"  Entropy (H):                    {analise_zhang.H_entropy:.4f}")
    print(f"  Classificação:                  {analise_zhang.classificacao_acoplamento()}\n")
    
    print(f"METODOLOGIA 2: Dou et al. (2023) - VRM Model")
    print(f"  Coupling                  (C):  {analise_dou.C_vrm:.4f}")
    print(f"  Hierarchical Coefficient  (HC): {analise_dou.HC_vrm:.4f}")
    print(f"  Standart Coefficient      (SC): {analise_dou.SC_vrm:.4f}")
    print(f"  Classificação:                  {analise_dou.classificacao_acoplamento()}\n")
    
    print(f"{'='*70}")
    print(f"📄 Relatórios HTML gerados:\n")
    print(f"  1. report/analise_automatica_zhang.html")
    print(f"  2. report/analise_automatica_dou.html")
    print(f"\n💡 Abra os relatórios no navegador!")


if __name__ == "__main__":
    main()
