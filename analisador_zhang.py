#!/usr/bin/env python3
"""
Metodologia de Zhang et al. (2011)
Entropy Model + Judgment Matrix Model
"""

import math
import numpy as np
from datetime import datetime


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
        """Calcula Entropy Model"""
        H_total = 0.0
        detalhado = []

        for i, funcao in enumerate(self.funcoes):
            ni = float(self.graus[i])
            pi = self.probabilidades[funcao]

            if ni > 0 and pi > 0 and self.M > 0:
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
                <thead><tr><th>Função</th><th>Grau (ni)</th><th>Prob. (pi)</th><th>Termo</th></tr></thead>
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
