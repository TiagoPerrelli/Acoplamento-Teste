# 🚀 GUIA COMPLETO - ANALISADOR AUTOMÁTICO DE ACOPLAMENTO

## 📋 O que é?

Um analisador que **automaticamente**:
- ✅ Lê seu código Python
- ✅ Identifica funções e classes
- ✅ Detecta todos os acoplamentos
- ✅ Calcula métricas
- ✅ Gera HTML interativo com visualização

**Sem necessidade de configuração manual!**

---

## 🎯 Instalação

Nenhuma! O código usa apenas bibliotecas padrão do Python:
- `ast` (Abstract Syntax Tree - análise de código)
- `json` (geração de dados)
- `dataclasses` (estruturas de dados)

---

## 💡 Como Usar

### **Método 1: Analisar um Arquivo Python**

```python
from analisador_automatico import AutomaticCouplingAnalyzer

# Criar analisador
analyzer = AutomaticCouplingAnalyzer()

# Analisar arquivo
analyzer.analyze_file("meu_modulo.py")

# Ver resumo no console
analyzer.print_summary()

# Gerar HTML interativo
analyzer.generate_html_report("relatorio.html")
```

### **Método 2: Analisar Código Diretamente**

```python
from analisador_automatico import AutomaticCouplingAnalyzer

codigo = '''
class SensorData:
    def __init__(self):
        self.value = 0
    
    def read(self):
        return self.value
    
    def process(self):
        return self.read() * 2

class DataProcessor:
    def __init__(self, sensor):
        self.sensor = sensor
    
    def analyze(self):
        data = self.sensor.read()
        return data + 10
'''

analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_code(codigo, "MeuSistema")
analyzer.print_summary()
analyzer.generate_html_report("analise.html")
```

---

## 📊 O que o Analisador Detecta

### **1. Control Coupling (Acoplamento de Controle)**
- Chamadas de função
- Chamadas de método
- Fluxo de execução

**Exemplo detectado:**
```python
def funcA():
    funcB()  # ← CONTROL COUPLING detectado!

def funcB():
    pass
```

### **2. Data Coupling (Acoplamento de Dados)**
- Parâmetros compartilhados
- Variáveis globais
- Valores de retorno

**Exemplo detectado:**
```python
global_var = 0

def funcA():
    global global_var  # ← DATA COUPLING detectado!
    global_var = 10

def funcB():
    global global_var  # ← DATA COUPLING detectado!
    return global_var
```

### **3. Hybrid Data-Control Coupling**
- Combinação de control + data
- Chamadas com passagem de dados

**Exemplo detectado:**
```python
def mmc(a, b):
    return a * b // mdc(a, b)  # ← HYBRID COUPLING!
    #                └─ Chama mdc() E usa seu retorno

def mdc(a, b):
    return a if b == 0 else mdc(b, a % b)
```

---

## 📈 Métricas Calculadas

### **Métricas Gerais**
- ✓ **Acoplamento Total**: Soma de todos os acoplamentos
- ✓ **Acoplamento Médio**: Média entre funções/classes
- ✓ **Número de Funções**: Quantidade analisada
- ✓ **Número de Acoplamentos**: Total de dependências
- ✓ **Índice de Coesão**: 0-100% (quanto maior, melhor)

### **Métricas Detalhadas**
- ✓ **Acoplamento por Tipo**: data, control, hybrid
- ✓ **Funções Mais Acopladas**: Ranking
- ✓ **Matriz de Acoplamento**: Grau entre cada par

---

## 🎨 Relatório HTML Gerado

O HTML inclui:

### **1. Painel de Métricas** (Cards coloridos)
- Número de funções
- Acoplamentos detectados
- Acoplamento total
- Índice de coesão

### **2. Matriz Interativa**
- Cores por grau (verde → vermelho)
- Clique para ver detalhes
- Hover para preview

### **3. Detalhes de Acoplamentos**
- Lista completa
- Tipo de cada acoplamento
- Descrição
- Linha de código

### **4. Lista de Funções**
- Parâmetros
- Tipo de retorno
- Funções chamadas
- Número da linha

---

## 🔍 Exemplos Práticos

### **Exemplo 1: Sistema Simples**

```python
# arquivo: calculadora.py
def somar(a, b):
    return a + b

def multiplicar(a, b):
    return a * b

def potencia(base, exp):
    resultado = 1
    for _ in range(exp):
        resultado = multiplicar(resultado, base)  # ← Acoplamento aqui!
    return resultado
```

**Executar análise:**
```python
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("calculadora.py")
analyzer.print_summary()
# ✓ Funções analisadas: 3
# ✓ Acoplamentos: 1 (potencia → multiplicar)
# ✓ Tipo: hybrid_data_control
```

### **Exemplo 2: Classes e Métodos**

```python
# arquivo: sensor_system.py
class Sensor:
    def __init__(self):
        self.data = []
    
    def read(self):
        return len(self.data)
    
    def clear(self):
        self.data = []

class Monitor:
    def __init__(self, sensor):
        self.sensor = sensor
    
    def check(self):
        value = self.sensor.read()  # ← Acoplamento!
        if value > 100:
            self.sensor.clear()  # ← Acoplamento!
        return value
```

**Executar análise:**
```python
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("sensor_system.py")
analyzer.generate_html_report("sensor_analysis.html")
# Abre sensor_analysis.html no navegador!
```

---

## ⚙️ Interpretação dos Resultados

### **Índice de Coesão**

| Valor | Interpretação | Ação |
|-------|--------------|------|
| 90-100% | ✅ Excelente | Manter |
| 75-90% | 📋 Bom | Monitorar |
| 50-75% | ⚠️ Aceitável | Revisar |
| <50% | ❌ Deficiente | Refatorar |

### **Grau de Acoplamento**

| Grau | Cor no HTML | Severidade |
|------|-------------|-----------|
| 0.0-1.0 | 🟢 Verde | Baixo |
| 1.0-1.5 | 🟡 Amarelo | Moderado |
| 1.5-2.0 | 🟠 Laranja | Alto |
| >2.0 | 🔴 Vermelho | Crítico |

---

## 📚 Casos de Uso Reais

### **1. Auditoria de Código Legado**
```python
# Analisar sistema antigo
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("legacy_system.py")
metrics = analyzer.calculate_metrics()

if metrics['cohesion_index'] < 0.5:
    print("⚠️ Sistema precisa de refatoração!")
```

### **2. Code Review Automatizado**
```python
# Integrar no CI/CD
import sys

analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file(sys.argv[1])
metrics = analyzer.calculate_metrics()

if metrics['total_coupling'] > 50:
    print("❌ Acoplamento muito alto!")
    sys.exit(1)
```

### **3. Comparação Antes/Depois de Refatoração**
```python
# Antes
analyzer_before = AutomaticCouplingAnalyzer()
analyzer_before.analyze_file("codigo_original.py")
metrics_before = analyzer_before.calculate_metrics()

# Depois
analyzer_after = AutomaticCouplingAnalyzer()
analyzer_after.analyze_file("codigo_refatorado.py")
metrics_after = analyzer_after.calculate_metrics()

# Comparar
melhoria = (metrics_after['cohesion_index'] - 
            metrics_before['cohesion_index']) * 100
print(f"Melhoria na coesão: {melhoria:.1f}%")
```

---

## 🎓 Limitações e Considerações

### **O que o analisador PODE fazer:**
✅ Detectar chamadas diretas de função
✅ Identificar parâmetros compartilhados
✅ Rastrear variáveis globais
✅ Analisar métodos de classes
✅ Gerar métricas quantitativas

### **O que o analisador NÃO pode (ainda):**
❌ Analisar imports de outros módulos
❌ Detectar acoplamento via reflexão (getattr, eval)
❌ Analisar código gerado dinamicamente
❌ Considerar herança complexa
❌ Detectar acoplamento temporal

### **Melhorias Futuras Possíveis:**
🔧 Suporte a múltiplos arquivos
🔧 Análise de imports
🔧 Detecção de padrões de design
🔧 Integração com IDEs
🔧 Exportação para PDF/CSV

---

## 🛠️ Personalização

### **Ajustar Graus de Acoplamento**

Edite o método `_analyze_coupling`:

```python
def _analyze_coupling(self, source, target):
    # Mudar grau de control coupling
    self.couplings.append(CouplingInfo(
        ...,
        degree=1.5,  # ← Era 1.0, agora 1.5
        ...
    ))
```

### **Adicionar Novos Tipos de Detecção**

```python
def _detect_couplings(self):
    self.couplings = []
    
    for func_name, func_info in self.functions.items():
        for called_func in func_info.calls:
            if called_func in self.functions:
                self._analyze_coupling(...)
        
        # ← Adicione sua detecção aqui!
        # Exemplo: detectar uso de decorators
```

---

## 📞 Troubleshooting

### **Erro: "FileNotFoundError"**
```python
# Certifique-se do caminho correto
analyzer.analyze_file("./caminho/para/arquivo.py")
```

### **Erro: "SyntaxError"**
```python
# Código deve ser Python válido
# Corrija erros de sintaxe antes de analisar
```

### **Nenhum acoplamento detectado**
```python
# Verifique se há chamadas de função:
# - Funções devem chamar outras funções do mesmo arquivo
# - Análise é limitada a um arquivo por vez (por enquanto)
```

---

## 🎉 Resumo

**Em 3 linhas de código:**
```python
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("seu_codigo.py")
analyzer.generate_html_report("relatorio.html")
```

**Você terá:**
- ✅ Análise completa de acoplamento
- ✅ Métricas quantitativas
- ✅ Relatório visual interativo
- ✅ Identificação de pontos críticos

---

## 📄 Licença

Este código é de uso livre para fins educacionais e profissionais.

---

**Desenvolvido para análise de acoplamento conforme DO-178C e padrões de software aeronáutico.**

Data: Novembro 2025
