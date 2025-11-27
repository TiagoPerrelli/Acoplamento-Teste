import ast
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


@dataclass
class ElementaryCoupling:
    """
    Representa o elementary coupling de um dado d entre duas funções,
    seguindo Briand et al. "On the concept of coupling, its modeling and measurement".

    EC[d] = C[d] * PC[d] * N[d]

    - C[d]  = complexidade do dado
    - PC[d] = uso do dado para controle (program control)
    - N[d]  = número de conexões em que esse dado participa
    """
    source: str      # função/módulo que depende (quem chama)
    target: str      # função/módulo chamado
    data_name: str   # identificador do dado (parâmetro, variável, etc.)
    C: float         # complexidade do dado
    PC: float        # peso de controle
    N: float         # número de conexões que usam esse dado
    value: float = 0.0  # EC[d]

    def compute_value(self) -> float:
        # Fórmula exata do artigo: EC[d] = C[d] * PC[d] * N[d]
        self.value = self.C * self.PC * self.N
        return self.value


@dataclass
class ModuleCoupling:
    """
    Acoplamento de um módulo/função:
    MC(m) = soma dos EC[d] de todos os dados de conexão de saída de m.
    Aqui, saída = conexões em que m é o SOURCE (quem chama/usa).
    """
    element: str
    elementary: List[ElementaryCoupling] = field(default_factory=list)

    @property
    def total_coupling(self) -> float:
        return sum(ec.value for ec in self.elementary)


class CouplingVisitor(ast.NodeVisitor):
    """
    Visitor de AST que coleta:
      - em qual função estamos (current_function)
      - chamadas de função: (source, target, lista_de_nomes_de_argumentos)
    """
    def __init__(self):
        self.current_function: Optional[str] = None
        self.calls: List[Tuple[str, str, List[str]]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = prev

    def visit_Call(self, node: ast.Call):
        if self.current_function and isinstance(node.func, ast.Name):
            called = node.func.id
            arg_names: List[str] = []
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    arg_names.append(arg.id)
                else:
                    # para constantes ou expressões, usamos uma representação textual
                    arg_names.append(ast.dump(arg))
            self.calls.append((self.current_function, called, arg_names))
        self.generic_visit(node)


class CouplingAnalyzer:
    """
    Analisador automático baseado em:
    - fórmula de elementary coupling de Briand et al.
    - acoplamento atribuído à função SOURCE (quem chama/usa).
    """
    def __init__(self):
        self.elementary: List[ElementaryCoupling] = []

    def analyze_source(self, source: str):
        """
        Analisa o código-fonte Python (como string).
        Extrai chamadas e constrói os elementary couplings.
        """
        tree = ast.parse(source)
        visitor = CouplingVisitor()
        visitor.visit(tree)

        # Contar N[d]: quantas vezes cada "dado" aparece como dado de conexão
        data_usage_count: Dict[str, int] = defaultdict(int)
        for _, _, args in visitor.calls:
            for name in args:
                data_usage_count[name] += 1

        # Para cada chamada, criar EC[d] para cada dado de conexão
        for src, tgt, args in visitor.calls:
            for data_name in args:
                N_d = float(data_usage_count[data_name])
                ec = self._build_ec_from_call(src, tgt, data_name, N_d)
                ec.compute_value()
                self.elementary.append(ec)

    def analyze_file(self, filename: str, encoding: str = "utf-8"):
        """
        Analisa um arquivo .py diretamente.
        """
        with open(filename, "r", encoding=encoding) as f:
            source = f.read()
        self.analyze_source(source)

    def _build_ec_from_call(
        self,
        src: str,
        tgt: str,
        data_name: str,
        N_d: float,
    ) -> ElementaryCoupling:
        """
        Aqui você ajusta os atributos C[d] e PC[d] de acordo com a forma
        como quer aplicar o artigo ao seu contexto.

        - C[d]: complexidade do dado (pode ser 1 para tipos simples, maior para estruturas).
        - PC[d]: se o dado é usado para controle (flags, parâmetros que afetam fluxo, etc.).
        - N[d]: já calculado (quantas conexões usam esse dado).

        Neste exemplo inicial:
        - C[d] = 1.0 para todos (inteiros, listas simples, etc.).
        - PC[d] = 1.0 assumindo que não é dado de controle.
        Você pode depois refinar isso manualmente ou com regras.
        """
        C_d = 1.0
        PC_d = 1.0

        return ElementaryCoupling(
            source=src,
            target=tgt,
            data_name=data_name,
            C=C_d,
            PC=PC_d,
            N=N_d,
        )

    def aggregate_by_module(self) -> Dict[str, ModuleCoupling]:
        """
        Agrupa os elementary couplings por função SOURCE,
        seguindo a convenção de que o módulo acoplado é quem depende (quem chama).
        """
        results: Dict[str, ModuleCoupling] = defaultdict(lambda: ModuleCoupling(element=""))
        for ec in self.elementary:
            key = ec.source  # SOURCE = quem chama/usa
            if results[key].element == "":
                results[key].element = key
            results[key].elementary.append(ec)
        return results

    def print_report(self):
        """
        Imprime um relatório textual simples no console.
        """
        modules = self.aggregate_by_module()
        for name, mc in modules.items():
            print(f"Função {name}: coupling total = {mc.total_coupling:.3f}")
            for ec in mc.elementary:
                print(
                    f"  EC[{ec.data_name}] ({ec.source} → {ec.target}) = {ec.value:.3f}  "
                    f"[C={ec.C}, PC={ec.PC}, N={ec.N}]"
                )
            print()

    def generate_html_report(self, filename: str):
        """
        Gera um relatório HTML simples com:
        - tabela de funções e seus couplings
        - tabela de elementary couplings
        """
        modules = self.aggregate_by_module()

        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='pt-BR'>")
        html.append("<head>")
        html.append("<meta charset='UTF-8'>")
        html.append("<title>Relatório de Coupling (Briand et al.)</title>")
        html.append("""
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
            th { background-color: #f0f0f0; }
            .low { background-color: #e0ffe0; }
            .medium { background-color: #fff7cc; }
            .high { background-color: #ffd6d6; }
            code { background-color: #f7f7f7; padding: 2px 4px; border-radius: 3px; }
        </style>
        """)
        html.append("</head>")
        html.append("<body>")
        html.append("<h1>Relatório de Acoplamento (Briand et al.)</h1>")
        html.append("<p>Fórmula usada para elementary coupling: "
                    "de>EC[d] = C[d] × PC[d] × N[d]</code></p>")

        # Tabela de acoplamento por função
        html.append("<h2>Coupling por Função (SOURCE)</h2>")
        html.append("<table>")
        html.append("<tr><th>Função</th><th>Coupling Total</th><th>Nº de EC[d]</th></tr>")

        for name, mc in modules.items():
            total = mc.total_coupling
            # classificação simples de severidade só para visual:
            if total == 0:
                css = ""
            elif total < 3:
                css = "low"
            elif total < 6:
                css = "medium"
            else:
                css = "high"
            html.append(
                f"<tr class='{css}'>"
                f"<td>{name}</td>"
                f"<td>{total:.3f}</td>"
                f"<td>{len(mc.elementary)}</td>"
                f"</tr>"
            )

        html.append("</table>")

        # Tabela detalhada de EC[d]
        html.append("<h2>Elementary Couplings (EC[d])</h2>")
        html.append("<table>")
        html.append("<tr>"
                    "<th>Source</th>"
                    "<th>Target</th>"
                    "<th>Dado d</th>"
                    "<th>C[d]</th>"
                    "<th>PC[d]</th>"
                    "<th>N[d]</th>"
                    "<th>EC[d]</th>"
                    "</tr>")

        for name, mc in modules.items():
            for ec in mc.elementary:
                html.append(
                    "<tr>"
                    f"<td>{ec.source}</td>"
                    f"<td>{ec.target}</td>"
                    f"<td>{ec.data_name}</td>"
                    f"<td>{ec.C}</td>"
                    f"<td>{ec.PC}</td>"
                    f"<td>{ec.N}</td>"
                    f"<td>{ec.value:.3f}</td>"
                    "</tr>"
                )

        html.append("</table>")
        html.append("</body></html>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(html))


if __name__ == "__main__":
    # Exemplo simples com mdc/mmc/mdc_lista/mmc_lista
    codigo_exemplo = """
def mdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mmc(a, b):
    return abs(a * b) // mdc(a, b)

def mdc_lista(numeros):
    from functools import reduce
    return reduce(mdc, numeros)

def mmc_lista(numeros):
    from functools import reduce
    return reduce(mmc, numeros)
"""

    analyzer = CouplingAnalyzer()
    #analyzer.analyze_source(codigo_exemplo)
    analyzer.analyze_file("exemplo_desacoplado.py")
    analyzer.print_report()
    analyzer.generate_html_report("Report2/relatorio_coupling_desac.html")
    print("Relatório HTML gerado em 'relatorio_coupling.html'.")
