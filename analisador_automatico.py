#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALISADOR AUTOMÁTICO DE ACOPLAMENTO
====================================

Este módulo analisa código Python automaticamente e:
1. Identifica funções, classes e métodos
2. Detecta acoplamentos (data, control, hybrid)
3. Calcula métricas de acoplamento
4. Gera HTML interativo com visualização

Uso:
    analyzer = AutomaticCouplingAnalyzer()
    analyzer.analyze_file("meu_codigo.py")
    analyzer.generate_html_report("relatorio.html")
"""

import ast
import inspect
import json
from typing import Dict, List, Set, Tuple, Any
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class FunctionInfo:
    """Informações sobre uma função ou método"""
    name: str
    module: str
    params: List[str]
    returns: str
    calls: List[str]  # Funções que esta função chama
    variables_read: Set[str]
    variables_write: Set[str]
    is_method: bool = False
    class_name: str = None
    lineno: int = 0


@dataclass
class CouplingInfo:
    """Informação sobre um acoplamento detectado"""
    source: str
    target: str
    coupling_type: str  # 'data', 'control', 'hybrid_data_control'
    subtype: str
    degree: float
    description: str
    line_number: int = 0


class AutomaticCouplingAnalyzer:
    """
    Analisador automático de acoplamento em código Python.
    
    Detecta:
    - Chamadas de função (control coupling)
    - Parâmetros compartilhados (data coupling)
    - Variáveis globais (data coupling)
    - Retornos de função (data coupling)
    - Combinações (hybrid coupling)
    """
    
    def __init__(self):
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, List[str]] = {}  # class_name -> [methods]
        self.global_vars: Set[str] = set()
        self.couplings: List[CouplingInfo] = []
        self.source_code: str = ""
        self.module_name: str = ""
    
    def analyze_file(self, filepath: str):
        """Analisa um arquivo Python e detecta acoplamentos"""
        filepath = Path(filepath)
        self.module_name = filepath.stem
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.source_code = f.read()
        
        # Parse do código
        tree = ast.parse(self.source_code)
        
        # Primeira passagem: coletar informações sobre funções e classes
        self._collect_definitions(tree)
        
        # Segunda passagem: detectar acoplamentos
        self._detect_couplings()
        
        return self
    
    def analyze_code(self, code: str, module_name: str = "module"):
        """Analisa código Python diretamente (string)"""
        self.module_name = module_name
        self.source_code = code
        
        tree = ast.parse(code)
        self._collect_definitions(tree)
        self._detect_couplings()
        
        return self
    
    def _collect_definitions(self, tree: ast.AST):
        """Coleta definições de funções e classes"""
        
        class DefinitionCollector(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.current_class = None
            
            def visit_ClassDef(self, node):
                self.analyzer.classes[node.name] = []
                old_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = old_class
            
            def visit_FunctionDef(self, node):
                func_info = self._extract_function_info(node)
                self.analyzer.functions[func_info.name] = func_info
                
                if self.current_class:
                    self.analyzer.classes[self.current_class].append(func_info.name)
            
            def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
                # Extrair parâmetros
                params = [arg.arg for arg in node.args.args]
                
                # Extrair tipo de retorno (se anotado)
                returns = "Any"
                if node.returns:
                    returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else "Any"
                
                # Detectar chamadas de função
                calls = []
                variables_read = set()
                variables_write = set()
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            calls.append(child.func.attr)
                    
                    elif isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store):
                            variables_write.add(child.id)
                        elif isinstance(child.ctx, ast.Load):
                            variables_read.add(child.id)
                
                return FunctionInfo(
                    name=node.name,
                    module=self.analyzer.module_name,
                    params=params,
                    returns=returns,
                    calls=calls,
                    variables_read=variables_read,
                    variables_write=variables_write,
                    is_method=self.current_class is not None,
                    class_name=self.current_class,
                    lineno=node.lineno
                )
        
        collector = DefinitionCollector(self)
        collector.visit(tree)
    
    def _detect_couplings(self):
        """Detecta acoplamentos entre funções"""
        self.couplings = []
        
        for func_name, func_info in self.functions.items():
            # Para cada função chamada
            for called_func in func_info.calls:
                if called_func in self.functions:
                    self._analyze_coupling(func_info, self.functions[called_func])
    
    def _analyze_coupling(self, source: FunctionInfo, target: FunctionInfo):
        """Analisa o acoplamento entre duas funções"""
        
        # 1. Control Coupling: chamada de função
        self.couplings.append(CouplingInfo(
            source=source.name,
            target=target.name,
            coupling_type='control',
            subtype='function_call',
            degree=1.0,
            description=f"{source.name}() chama {target.name}()",
            line_number=source.lineno
        ))
        
        # 2. Data Coupling: parâmetros compartilhados
        shared_params = set(source.params) & set(target.params)
        if shared_params:
            self.couplings.append(CouplingInfo(
                source=source.name,
                target=target.name,
                coupling_type='data',
                subtype='shared_parameters',
                degree=1.5,
                description=f"Parâmetros compartilhados: {', '.join(shared_params)}",
                line_number=source.lineno
            ))
        
        # 3. Data Coupling: variáveis compartilhadas
        shared_vars = (source.variables_read | source.variables_write) & \
                      (target.variables_read | target.variables_write)
        shared_vars = shared_vars - set(source.params) - set(target.params)
        
        if shared_vars:
            self.couplings.append(CouplingInfo(
                source=source.name,
                target=target.name,
                coupling_type='data',
                subtype='shared_variables',
                degree=1.8,
                description=f"Variáveis compartilhadas: {', '.join(shared_vars)}",
                line_number=source.lineno
            ))
        
        # 4. Hybrid Coupling: se há chamada E compartilhamento de dados
        if target.name in source.calls and (shared_params or shared_vars):
            self.couplings.append(CouplingInfo(
                source=source.name,
                target=target.name,
                coupling_type='hybrid_data_control',
                subtype='call_with_data_sharing',
                degree=2.0,
                description=f"Chamada com compartilhamento de dados",
                line_number=source.lineno
            ))
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de acoplamento"""
        if not self.couplings:
            return {
                'total_coupling': 0,
                'average_coupling': 0,
                'num_functions': len(self.functions),
                'num_couplings': 0,
                'cohesion_index': 1.0,
                'coupling_by_type': {},
                'function_coupling': {}
            }
        
        total_coupling = sum(c.degree for c in self.couplings)
        avg_coupling = total_coupling / len(self.couplings)
        
        # Acoplamento por tipo
        coupling_by_type = defaultdict(float)
        for c in self.couplings:
            coupling_by_type[c.coupling_type] += c.degree
        
        # Acoplamento por função
        function_coupling = defaultdict(float)
        for c in self.couplings:
            function_coupling[c.source] += c.degree
            function_coupling[c.target] += c.degree
        
        # Índice de coesão
        n = len(self.functions)
        max_possible = n * (n - 1) if n > 1 else 1
        cohesion = 1 - (total_coupling / max_possible) if max_possible > 0 else 1.0
        
        return {
            'total_coupling': total_coupling,
            'average_coupling': avg_coupling,
            'num_functions': n,
            'num_couplings': len(self.couplings),
            'cohesion_index': cohesion,
            'coupling_by_type': dict(coupling_by_type),
            'function_coupling': dict(sorted(function_coupling.items(), 
                                            key=lambda x: x[1], reverse=True))
        }
    
    def generate_coupling_matrix(self) -> Dict[str, Dict[str, float]]:
        """Gera matriz de acoplamento"""
        func_names = list(self.functions.keys())
        matrix = {f1: {f2: 0.0 for f2 in func_names} for f1 in func_names}
        
        for coupling in self.couplings:
            current = matrix[coupling.source][coupling.target]
            matrix[coupling.source][coupling.target] = max(current, coupling.degree)
            matrix[coupling.target][coupling.source] = max(current, coupling.degree)
        
        return matrix
    
    def generate_html_report(self, output_file: str = "coupling_report.html"):
        """Gera relatório HTML interativo"""
        metrics = self.calculate_metrics()
        matrix = self.generate_coupling_matrix()
        
        # Preparar dados para JSON
        functions_data = []
        for fname, finfo in self.functions.items():
            functions_data.append({
                'name': fname,
                'params': finfo.params,
                'returns': finfo.returns,
                'calls': finfo.calls,
                'is_method': finfo.is_method,
                'class_name': finfo.class_name,
                'line': finfo.lineno
            })
        
        couplings_data = [
            {
                'source': c.source,
                'target': c.target,
                'type': c.coupling_type,
                'subtype': c.subtype,
                'degree': c.degree,
                'description': c.description,
                'line': c.line_number
            }
            for c in self.couplings
        ]
        
        html_content = self._generate_html_template(
            functions_data, couplings_data, metrics, matrix
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Relatório HTML gerado: {output_file}")
        return output_file
    
    def _generate_html_template(self, functions, couplings, metrics, matrix):
        """Template HTML para o relatório"""
        
        functions_json = json.dumps(functions, indent=2)
        couplings_json = json.dumps(couplings, indent=2)
        metrics_json = json.dumps(metrics, indent=2)
        matrix_json = json.dumps(matrix, indent=2)
        
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise Automática de Acoplamento</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .section {{
            margin: 30px 0;
        }}
        
        .section-title {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .matrix-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th, td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #ddd;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: bold;
        }}
        
        td {{
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        td:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }}
        
        .coupling-low {{ background: #d4edda; }}
        .coupling-medium {{ background: #fff3cd; }}
        .coupling-high {{ background: #f8d7da; }}
        .coupling-critical {{ background: #f5c6cb; font-weight: bold; }}
        
        .function-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .function-card {{
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9ff;
        }}
        
        .function-name {{
            color: #667eea;
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .function-info {{
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }}
        
        .coupling-details {{
            margin-top: 20px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .coupling-item {{
            padding: 10px;
            margin: 10px 0;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #764ba2;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 5px;
        }}
        
        .badge-data {{ background: #d4edda; color: #155724; }}
        .badge-control {{ background: #d1ecf1; color: #0c5460; }}
        .badge-hybrid {{ background: #fff3cd; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Análise Automática de Acoplamento</h1>
        <p class="subtitle">Módulo: <strong>{self.module_name}</strong></p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Funções Analisadas</div>
                <div class="metric-value" id="num-functions">{metrics['num_functions']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Acoplamentos Detectados</div>
                <div class="metric-value" id="num-couplings">{metrics['num_couplings']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Acoplamento Total</div>
                <div class="metric-value" id="total-coupling">{metrics['total_coupling']:.1f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Índice de Coesão</div>
                <div class="metric-value" id="cohesion">{metrics['cohesion_index']*100:.1f}%</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 Matriz de Acoplamento</h2>
            <div class="matrix-container" id="matrix-container"></div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔗 Detalhes dos Acoplamentos</h2>
            <div id="couplings-container"></div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📝 Funções Analisadas</h2>
            <div class="function-list" id="functions-list"></div>
        </div>
    </div>
    
    <script>
        const functions = {functions_json};
        const couplings = {couplings_json};
        const metrics = {metrics_json};
        const matrix = {matrix_json};
        
        // Renderizar matriz
        function renderMatrix() {{
            const container = document.getElementById('matrix-container');
            const funcNames = Object.keys(matrix);
            
            let html = '<table><thead><tr><th>Função</th>';
            funcNames.forEach(name => {{
                html += `<th>${{name.substring(0, 10)}}</th>`;
            }});
            html += '</tr></thead><tbody>';
            
            funcNames.forEach(fname1 => {{
                html += `<tr><th>${{fname1}}</th>`;
                funcNames.forEach(fname2 => {{
                    const value = matrix[fname1][fname2];
                    let className = '';
                    if (fname1 === fname2) {{
                        html += '<td>-</td>';
                    }} else {{
                        if (value === 0) className = '';
                        else if (value < 1.0) className = 'coupling-low';
                        else if (value < 1.5) className = 'coupling-medium';
                        else if (value < 2.0) className = 'coupling-high';
                        else className = 'coupling-critical';
                        
                        html += `<td class="${{className}}" onclick="showCouplingDetails('${{fname1}}', '${{fname2}}')">${{value.toFixed(2)}}</td>`;
                    }}
                }});
                html += '</tr>';
            }});
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }}
        
        // Renderizar acoplamentos
        function renderCouplings() {{
            const container = document.getElementById('couplings-container');
            let html = '';
            
            couplings.forEach((c, idx) => {{
                const badgeClass = c.type === 'data' ? 'badge-data' : 
                                   c.type === 'control' ? 'badge-control' : 'badge-hybrid';
                
                html += `
                    <div class="coupling-item">
                        <strong>${{c.source}} → ${{c.target}}</strong>
                        <span class="badge ${{badgeClass}}">${{c.type}}</span>
                        <br>
                        <small>Grau: ${{c.degree.toFixed(2)}} | ${{c.description}}</small>
                    </div>
                `;
            }});
            
            container.innerHTML = html || '<p>Nenhum acoplamento detectado.</p>';
        }}
        
        // Renderizar funções
        function renderFunctions() {{
            const container = document.getElementById('functions-list');
            let html = '';
            
            functions.forEach(f => {{
                html += `
                    <div class="function-card">
                        <div class="function-name">${{f.name}}()</div>
                        <div class="function-info">Parâmetros: ${{f.params.join(', ') || 'Nenhum'}}</div>
                        <div class="function-info">Retorna: ${{f.returns}}</div>
                        <div class="function-info">Chama: ${{f.calls.join(', ') || 'Nenhuma'}}</div>
                        <div class="function-info">Linha: ${{f.line}}</div>
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        // Inicializar
        renderMatrix();
        renderCouplings();
        renderFunctions();
    </script>
</body>
</html>"""
    
    def print_summary(self):
        """Imprime resumo da análise"""
        metrics = self.calculate_metrics()
        
        print("\n" + "=" * 80)
        print(f"RESUMO DA ANÁLISE - Módulo: {self.module_name}")
        print("=" * 80)
        print(f"\n✓ Funções analisadas: {metrics['num_functions']}")
        print(f"✓ Acoplamentos detectados: {metrics['num_couplings']}")
        print(f"✓ Acoplamento total: {metrics['total_coupling']:.2f}")
        print(f"✓ Acoplamento médio: {metrics['average_coupling']:.2f}")
        print(f"✓ Índice de coesão: {metrics['cohesion_index']:.2%}")
        
        print("\n[Acoplamento por Tipo]")
        for ctype, degree in metrics['coupling_by_type'].items():
            print(f"  • {ctype}: {degree:.2f}")
        
        print("\n[Funções Mais Acopladas]")
        for func, degree in list(metrics['function_coupling'].items())[:5]:
            print(f"  • {func}: {degree:.2f}")
        
        print("\n" + "=" * 80)


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Código de exemplo para analisar
    exemplo_codigo = '''
def mdc(a: int, b: int) -> int:
    """Máximo Divisor Comum"""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def mmc(a: int, b: int) -> int:
    """Mínimo Múltiplo Comum"""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // mdc(a, b)

def mmc_lista(numeros):
    """MMC de lista"""
    if not numeros:
        return 0
    resultado = numeros[0]
    for num in numeros[1:]:
        resultado = mmc(resultado, num)
    return resultado

def mdc_lista(numeros):
    """MDC de lista"""
    if not numeros:
        return 0
    resultado = numeros[0]
    for num in numeros[1:]:
        resultado = mdc(resultado, num)
    return resultado
'''
    
    # Criar analisador
    analyzer = AutomaticCouplingAnalyzer()
    
    # Analisar código
    #analyzer.analyze_code(exemplo_codigo, "meu_modulo")
    analyzer.analyze_file("exemplo_acoplamento_alto.py")
    # Imprimir resumo
    analyzer.print_summary()
    
    # Gerar HTML
    analyzer.generate_html_report("Report1/Acoplado.html")
    
    print("\n✓ Análise completa!")
    print("✓ Abra 'analise_automatica.html' no navegador para ver o relatório interativo")
