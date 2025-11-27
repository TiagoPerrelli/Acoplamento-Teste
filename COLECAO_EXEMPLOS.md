# 🎓 COLEÇÃO DE EXEMPLOS - Analisador Automático de Acoplamento

## 📚 Exemplos Fornecidos

### **Exemplo 1: Funções Matemáticas (BÁSICO)**
**Arquivo:** `exemplo_mmc_mdc.py` (ou executar inline)  
**Complexidade:** ⭐ Iniciante  
**Conceito:** Acoplamento necessário por fórmula matemática

```python
def mdc(a, b): ...
def mmc(a, b): ...  # ← Depende de mdc() por fórmula
def mmc_lista(nums): ...  # ← Itera chamando mmc()
```

**Análise Esperada:**
- Acoplamentos: 7
- Tipo: Principalmente hybrid_data_control
- Coesão: ~12% (baixa, mas NECESSÁRIA)
- Função crítica: mmc() com grau 7.5

---

### **Exemplo 2: Pipeline de Processamento (INTERMEDIÁRIO)**
**Arquivo:** `exemplo_pipeline_dados.py`  
**Complexidade:** ⭐⭐ Intermediário  
**Conceito:** Chain of Responsibility pattern com acoplamento natural

```python
DataReader
    ↓ (depende)
DataValidator
    ↓ (depende)
DataProcessor
    ↓ (depende)
DataAnalyzer
    ↓ (depende)
ReportGenerator
```

**Análise Esperada:**
- Acoplamentos: 27+
- Tipo: Principalmente hybrid_data_control
- Coesão: ~85% (boa para padrão linear)
- Funções críticas: Validator, Processor, Analyzer

**Padrão:** Linear pipeline (aceitável)

---

### **Exemplo 3: Sistema Desacoplado (AVANÇADO - BOM DESIGN)**
**Arquivo:** `exemplo_desacoplado.py`  
**Complexidade:** ⭐⭐⭐ Avançado  
**Conceito:** Dependency Injection com interfaces (SOLID principles)

```python
Pipeline usa:
  - IDataSource (interface)
  - IValidator (interface)
  - IProcessor (interface)
  - IAnalyzer (interface)

NÃO conhece:
  - FileDataSource (implementação)
  - SimpleValidator (implementação)
  - DoubleProcessor (implementação)
  - StatisticsAnalyzer (implementação)
```

**Análise Esperada:**
- Acoplamentos: REDUZIDOS
- Tipo: Control coupling apenas
- Coesão: ~95% (EXCELENTE!)
- Função crítica: Pipeline.execute()

**Padrão:** Dependency Injection (RECOMENDADO)

---

### **Exemplo 4: Sistema Acoplado (PÉSSIMO - ANTIPADRÃO)**
**Arquivo:** `exemplo_acoplamento_alto.py`  
**Complexidade:** ⭐⭐ Intermediário (mas RUIM)  
**Conceito:** O que NÃO fazer - variáveis globais, alta interdependência

```python
GlobalState:
  - config, cache, errors, users, products, orders
  (COMPARTILHADO POR TODOS!)

UserManager
ProductManager  } todos modificam GlobalState
OrderManager
ReportGenerator
```

**Análise Esperada:**
- Acoplamentos: MUITOS
- Tipo: Principalmente data_coupling (via GlobalState)
- Coesão: Negativa! (-50% a -100%)
- Funções críticas: Praticamente TODAS

**Padrão:** ANTIPADRÃO (NÃO USAR)

---

## 🚀 Como Executar

### **Método 1: Analisar um arquivo específico**

```bash
# Analisar exemplo 2 (pipeline)
python analisador_automatico.py exemplo_pipeline_dados.py

# Analisar exemplo 3 (desacoplado)
python analisador_automatico.py exemplo_desacoplado.py

# Analisar exemplo 4 (acoplado - antipadrão)
python analisador_automatico.py exemplo_acoplamento_alto.py
```

### **Método 2: Analisar via Python**

```python
from analisador_automatico import AutomaticCouplingAnalyzer

# Analisar arquivo
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("exemplo_pipeline_dados.py")
analyzer.print_summary()
analyzer.generate_html_report("pipeline_analysis.html")

# Abrir no navegador
import webbrowser
webbrowser.open("pipeline_analysis.html")
```

### **Método 3: Analisar código inline**

```python
from analisador_automatico import AutomaticCouplingAnalyzer

codigo = '''
class ClassA:
    def metodo1(self):
        self.metodo2()
    
    def metodo2(self):
        pass
'''

analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_code(codigo, "MeuModulo")
analyzer.print_summary()
```

---

## 📊 Comparação dos Exemplos

| Aspecto | Ex1 (Math) | Ex2 (Pipeline) | Ex3 (Interfaces) | Ex4 (Antipadrão) |
|---------|-----------|----------------|-----------------|-----------------|
| Funções | 4 | 17 | 6 | 12 |
| Acoplamentos | 7 | 27 | ~5 | 50+ |
| Coesão | 12% | 85% | 95% | -50% |
| Complexidade | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Status | ✓ OK | ✓ BOM | ✓✓ EXCELENTE | ❌ RUIM |
| Padrão | Matemática | Pipeline | Dependency Inj. | Antipadrão |
| Recomendação | Usar | Usar | RECOMENDADO | EVITAR |

---

## 🎯 O que Aprender de Cada

### **Exemplo 1: Acoplamento Necessário**
- ✓ Nem todo acoplamento é ruim
- ✓ Acoplamento por fórmula/lógica é NECESSÁRIO
- ✓ Como documentar acoplamentos justificáveis

### **Exemplo 2: Padrão Linear Aceitável**
- ✓ Pipelines naturalmente têm alto acoplamento
- ✓ Acoplamento é ESPERADO e ACEITÁVEL
- ✓ Quando usar pipeline vs interfaces

### **Exemplo 3: Boas Práticas (SOLID)**
- ✓ Dependency Injection reduz acoplamento dramaticamente
- ✓ Interfaces permitem implementações intercambiáveis
- ✓ Código testável e extensível
- ✓ Segue princípios SOLID

### **Exemplo 4: O que NÃO Fazer**
- ❌ Variáveis globais = acoplamento invisível
- ❌ Estado compartilhado = dificuldade de testar
- ❌ Responsabilidades misturadas = código frágil
- ❌ Modificações quebram tudo

---

## 💡 Fluxo de Aprendizado Recomendado

1. **Comece com Exemplo 1** (5 minutos)
   - Entenda acoplamento básico
   - Veja como o analisador funciona

2. **Depois Exemplo 2** (15 minutos)
   - Estude padrão pipeline
   - Veja acoplamento natural
   - Compare com Exemplo 1

3. **Estude Exemplo 3** (20 minutos)
   - Aprenda Dependency Injection
   - Veja como reduzir acoplamento
   - Entenda SOLID principles

4. **Revise Exemplo 4** (10 minutos)
   - Veja o oposto do bom design
   - Identifique problemas
   - Aprenda o que EVITAR

---

## 🔍 Perguntas para Análise Pessoal

Após rodar cada exemplo, responda:

1. **Qual é o acoplamento crítico?**
   - Grau > 2.0 em qualquer exemplo?
   - Qual função tem mais acoplamento?

2. **O acoplamento é justificável?**
   - Por quê existe?
   - Poderia ser reduzido?
   - Deveria ser reduzido?

3. **Como melhorar?**
   - Usar interfaces?
   - Separar responsabilidades?
   - Aplicar padrão de design?

4. **Qual exemplo eu prefiro?**
   - Por quê?
   - Como aplicar conceitos no seu código?

---

## 🛠️ Exercício Prático

### **Desafio 1: Analisar seu próprio código**
```python
# Abra um arquivo .py seu
analyzer = AutomaticCouplingAnalyzer()
analyzer.analyze_file("seu_arquivo.py")
analyzer.generate_html_report()

# Questões:
# - Sua coesão é boa? (> 70%?)
# - Há acoplamentos críticos (> 2.0)?
# - Como você poderia refatorar?
```

### **Desafio 2: Refatorar Exemplo 2 para Exemplo 3**
```python
# Pegue código do Pipeline (Ex2)
# Converta para usar Interfaces (Ex3)
# Compare métricas:
#   Coesão melhora?
#   Acoplamentos diminuem?
#   Código fica mais fácil testar?
```

### **Desafio 3: Evitar Antipadrões**
```python
# Revise seu código
# Procure por:
#   - Variáveis globais
#   - Estado compartilhado
#   - Responsabilidades misturadas
# Refatore usando Exemplo 3 como guia
```

---

## 📚 Recursos Adicionais

### **Para Aprender Mais**
- SOLID Principles: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- Design Patterns: Factory, Strategy, Observer, Mediator
- Python Protocols: `typing.Protocol` para interfaces sem ABC

### **Ferramentas Relacionadas**
- `pylint`: Análise estática de código
- `radon`: Métricas de complexidade
- `mypy`: Type checking
- `pytest`: Testes unitários

---

## ✅ Checklist: Seu Código Está Bem?

- [ ] Coesão > 70%?
- [ ] Acoplamentos < 1.5 (maioria)?
- [ ] Sem acoplamentos críticos (> 2.5)?
- [ ] Responsabilidades claras?
- [ ] Interfaces bem definidas?
- [ ] Fácil de testar?
- [ ] Fácil de estender?
- [ ] Sem variáveis globais?

---

## 🎉 Conclusão

Você agora tem 4 exemplos práticos para:
1. **Entender** acoplamento em diferentes contextos
2. **Analisar** automaticamente seu código
3. **Comparar** diferentes abordagens
4. **Melhorar** qualidade de design

**Próximo passo:** Aplique o analisador em seu próprio código!

---

**Desenvolvido para aprendizado de acoplamento em software**  
Data: Novembro 2025
