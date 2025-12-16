#!/usr/bin/env python3
"""
Metodologia de Dou et al. (2023)
VRM Model (Variable Requirement Model) baseado em VARIÁVEIS
"""

import math
import numpy as np
from datetime import datetime
from collections import defaultdict


class AnalisadorDou:
    """Implementa metodologia de Dou et al. (2023) - VRM Model"""

    def __init__(self, variaveis_dict, manual_coefficients, var_dependencies):
        self.variaveis = list(variaveis_dict.keys())
        self.variaveis_dict = variaveis_dict
        self.n = len(self.variaveis)
        self.manual_coefficients = manual_coefficients
        self.var_dependencies = var_dependencies

        self.mc_values = {}
        self.sc_values = {}
        self.hc_values = {}

        self._calcular_coeficientes()
        self._calcular_acoplamento_vrm()

    def _calcular_coeficientes(self):
        """Calcula MC, SC e HC para cada variável"""

        # Manual Coefficient
        for var in self.variaveis:
            self.mc_values[var] = self.manual_coefficients.get(var, 1.0)

        # Standard Coefficient - FÓRMULA CORRETA
        # SC(i) = Xi + sqrt(Σ(Xj - μ)² / N)
        # Onde:
        #   Xi = frequência (total de usos) da variável i
        #   μ (mi) = média das frequências de todas as variáveis
        #   N = total de variáveis

        # Extrair Xi de cada variável
        frequencias = np.array([self.variaveis_dict[var]["frequencia"] for var in self.variaveis])
        mi = np.mean(frequencias)  # μ = média
        N = self.n  # N = total de variáveis

        # Calcular o desvio padrão: sqrt(Σ(Xj - μ)² / N)
        soma_quadrados = np.sum((frequencias - mi) ** 2)
        desvio = math.sqrt(soma_quadrados / N) if N > 0 else 0.0

        print(f"\n📊 Estatísticas SC:")
        print(f"   μ (média) = {mi:.2f}")
        print(f"   Desvio = {desvio:.2f}")
        print(f"   Faixa Xi: {frequencias.min()} a {frequencias.max()}")

        # Calcular SC para cada variável
        for i, var in enumerate(self.variaveis):
            Xi = float(frequencias[i])
            # SC(i) = Xi + sqrt(Σ(Xj - μ)² / N)
            self.sc_values[var] = Xi + desvio

        # Hierarchical Coefficient
        # HC(i) = (dep(i) + 1) × 1/(2^(dep(i)-1))

        profundidades = self._calcular_profundidades_arvore()

        for var in self.variaveis:
            dep_i = profundidades[var]

            # HC = (dep(i) + 1) × 1/(2^(dep(i)-1))
            self.hc_values[var] = (dep_i + 1) * (1.0 / (2.0 ** (dep_i - 1)))

    def _calcular_profundidades_arvore(self):
        """
        Calcula a profundidade de cada variável na árvore de dependências.
        dep(i) = distância em unidades do nó raiz (nó sem dependências).

        Exemplo: a = b + 1
        - 'b' é nó raiz (dep = 0)
        - 'a' depende de 'b', então dep(a) = 1
        """
        profundidades = {var: 0 for var in self.variaveis}

        # Identificar nós raiz (variáveis que não dependem de ninguém)
        nos_raiz = set()
        for var in self.variaveis:
            if var not in self.var_dependencies or len(self.var_dependencies[var]) == 0:
                nos_raiz.add(var)
                profundidades[var] = 0

        # BFS para calcular profundidades a partir dos nós raiz
        visitados = set(nos_raiz)
        fila = list(nos_raiz)

        while fila:
            var_atual = fila.pop(0)
            prof_atual = profundidades[var_atual]

            # Encontrar variáveis que dependem de var_atual
            for var_dependente in self.variaveis:
                if var_dependente in self.var_dependencies:
                    if var_atual in self.var_dependencies[var_dependente]:
                        # var_dependente depende de var_atual
                        nova_prof = prof_atual + 1

                        if var_dependente not in visitados:
                            profundidades[var_dependente] = nova_prof
                            visitados.add(var_dependente)
                            fila.append(var_dependente)
                        else:
                            # Atualizar se encontrou caminho mais longo
                            profundidades[var_dependente] = max(
                                profundidades[var_dependente], 
                                nova_prof
                            )

        return profundidades

    def _calcular_acoplamento_vrm(self):
        """Calcula Acoplamento total = Σ(MC + SC + HC)"""

        acoplamento_total = 0.0
        sc_total = 0.0
        hc_total = 0.0
        detalhado = []

        for var in self.variaveis:
            mc = self.mc_values[var]
            sc = self.sc_values[var]
            hc = self.hc_values[var]

            acoplamento = mc + sc + hc
            sc_total += sc
            hc_total += hc
            acoplamento_total += acoplamento

            detalhado.append({
                "variavel": var,
                "xi": self.variaveis_dict[var]["frequencia"],  # Mostrar Xi
                "mc": float(mc),
                "sc": float(sc),
                "hc": float(hc),
                "acoplamento": float(acoplamento)
            })

        self.C_vrm = float(acoplamento_total)
        self.C_medio = float(acoplamento_total / self.n)
        self.HC_medio = float(hc_total / self.n) if self.n > 0 else 0.0
        self.SC_medio = float(sc_total / self.n) if self.n > 0 else 0.0

        self.detalhado = detalhado


    def gerar_arvore_dependencias_html(self):
        """Gera visualização da árvore de dependências em HTML"""
        profundidades = self._calcular_profundidades_arvore()

        # Agrupar variáveis por profundidade
        por_nivel = defaultdict(list)
        for var in self.variaveis:
            nivel = profundidades[var]
            por_nivel[nivel].append(var)

        html = '<div style="background:#f9f9f9;padding:15px;border:1px solid #ccc;margin:15px 0;">'
        html += '<h3 style="margin-top:0;">Árvore de Dependências de Variáveis</h3>'
        html += '<p style="font-size:0.9em;color:#666;">dep(i) = distância do nó raiz (variáveis sem dependências)</p>'

        max_nivel = max(por_nivel.keys()) if por_nivel else 0

        for nivel in range(max_nivel + 1):
            vars_nivel = por_nivel.get(nivel, [])

            html += f'<div style="margin:10px 0;padding:10px;background:#fff;border-left:3px solid '

            if nivel == 0:
                html += '#4CAF50'  # Verde para raiz
            elif nivel == max_nivel:
                html += '#f44336'  # Vermelho para folhas
            else:
                html += '#2196F3'  # Azul para intermediários

            html += ';">'
            html += f'<strong>Nível {nivel} (dep = {nivel}):</strong> '

            if vars_nivel:
                vars_nomes = [v.split("::")[-1] for v in sorted(vars_nivel)]
                html += ', '.join(vars_nomes[:10])
                if len(vars_nivel) > 10:
                    html += f' <span style="color:#666;">(+{len(vars_nivel)-10} mais)</span>'
            else:
                html += '<em style="color:#999;">nenhuma variável</em>'

            html += '</div>'

        html += '</div>'
        return html


def gerar_html_dou(variaveis, analise_dou):
    """Gera relatório HTML para metodologia Dou et al. (2023)"""

    def format_coeficientes(detalhado):
        html = ""
        # Ordenar por acoplamento (maior primeiro)
        detalhado_ordenado = sorted(detalhado, key=lambda x: x['acoplamento'], reverse=True)

        for item in detalhado_ordenado[:30]:
            var_nome = item['variavel'].split("::")[-1]
            funcao = item['variavel'].split("::")[0].split(".")[-1]
            html += f"""<tr>
                <td style="font-size:0.9em;">{var_nome}</td>
                <td style="font-size:0.85em;color:#666;">{funcao}</td>
                <td style="text-align:center;color:#2196F3;font-weight:bold;">{item['xi']}</td>
                <td style="text-align:center;">{item['mc']:.2f}</td>
                <td style="text-align:center;">{item['sc']:.4f}</td>
                <td style="text-align:center;">{item['hc']:.4f}</td>
                <td style="text-align:center;font-weight:bold;">{item['acoplamento']:.4f}</td>
            </tr>"""

        if len(detalhado) > 30:
            html += f'<tr><td colspan="7" style="text-align:center;padding:4px;color:#666;">... e mais {len(detalhado)-30} variáveis</td></tr>'
        return html

    # Gerar árvore de dependências
    arvore_html = analise_dou.gerar_arvore_dependencias_html()

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
        .formula{{background:#fff;padding:10px;border:1px solid #ddd;margin:10px 0;font-family:monospace;}}
        footer{{border-top:1px solid #999;padding-top:15px;margin-top:30px;color:#666;font-size:0.9em;text-align:center;}}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Análise de Acoplamento: Dou et al. (2023)</h1>
            <p class="subtitle">VRM Model (Variable Requirement Model)</p>
            <p class="subtitle">Baseado em VARIÁVEIS do sistema</p>
            <p class="subtitle">Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </header>

        <section>
            <h2>Resumo</h2>
            <table>
                <tr><td><strong>Total de Variáveis</strong></td><td>{len(variaveis)}</td></tr>
                <tr><td><strong>Variáveis Analisadas</strong></td><td>{len(analise_dou.detalhado)}</td></tr>
            </table>
        </section>

        <section>
            <h2>Resultados Principais (VRM Model)</h2>
            <div class="metric">
                <div class="metric-label">Acoplamento Médio Total (C):</div>
                <div class="metric-value">{analise_dou.C_medio:.4f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">HC Médio:</div>
                <div class="metric-value">{analise_dou.HC_medio:.4f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">SC Médio:</div>
                <div class="metric-value">{analise_dou.SC_medio:.4f}</div>
            </div>
        </section>

        <section>
            <h2>Árvore de Dependências</h2>
            {arvore_html}
        </section>

        <section>
            <h2>Fórmulas Aplicadas</h2>
            <div class="formula">
                <strong>SC (Standard Coefficient):</strong><br/>
                SC(i) = Xi + √(Σ(Xj - μ)² / N)<br/>
                <span style="font-size:0.85em;color:#666;">
                Onde: Xi = total de usos da variável i, μ = média dos usos, N = total de variáveis
                </span>
            </div>
            <div class="formula">
                <strong>HC (Hierarchical Coefficient):</strong><br/>
                HC(i) = (dep(i) + 1) × 1/(2^(dep(i)-1))<br/>
                <span style="font-size:0.85em;color:#666;">
                Onde: dep(i) = profundidade na árvore de dependências
                </span>
            </div>
            <div class="formula">
                <strong>Acoplamento Total:</strong><br/>
                C = Σ(MC + SC + HC) para todas as variáveis
            </div>
        </section>

        <section>
            <h2>Coeficientes VRM - Top 30 Variáveis</h2>
            <p class="note">Ordenado por acoplamento (maior → menor). Xi = total de usos da variável.</p>
            <table>
                <thead><tr><th>Variável</th><th>Função</th><th>Xi (usos)</th><th>MC</th><th>SC</th><th>HC</th><th>Acoplamento</th></tr></thead>
                <tbody>{format_coeficientes(analise_dou.detalhado)}</tbody>
            </table>
            <div class="highlight">
                <strong>Soma de todos os Acoplamento das variáveis do Sistema = {analise_dou.C_vrm:.4f}</strong>
            </div>
        </section>

        <footer>
            <p>Dou et al. (2023). A Coupling Analysis Method for Airborne Software Based on Requirement Model.</p>
        </footer>
    </div>
</body>
</html>"""

    return html_str
