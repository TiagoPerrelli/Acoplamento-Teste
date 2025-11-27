"""
EXEMPLO 3: Sistema Desacoplado com Interfaces
==============================================

Um exemplo com padrão de design melhorado, usando interfaces
para reduzir acoplamento em relação ao exemplo anterior.
"""

# ============================================================================
# INTERFACES (Protocolos) - Define contratos
# ============================================================================

from abc import ABC, abstractmethod
from typing import List, Dict

class IDataSource(ABC):
    """Interface para qualquer fonte de dados"""
    
    @abstractmethod
    def read(self) -> List[int]:
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        pass


class IValidator(ABC):
    """Interface para qualquer validador"""
    
    @abstractmethod
    def validate(self, data: List[int]) -> bool:
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        pass


class IProcessor(ABC):
    """Interface para qualquer processador"""
    
    @abstractmethod
    def process(self, data: List[int]) -> List[int]:
        pass


class IAnalyzer(ABC):
    """Interface para qualquer analisador"""
    
    @abstractmethod
    def analyze(self, data: List[int]) -> Dict:
        pass


# ============================================================================
# IMPLEMENTAÇÕES CONCRETAS - Usam interfaces
# ============================================================================

class FileDataSource(IDataSource):
    """Implementação concreta de leitura de arquivo"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.data = []
    
    def read(self) -> List[int]:
        """Lê dados do arquivo"""
        self.data = [10, 20, 30, 40, 50]
        return self.data
    
    def is_valid(self) -> bool:
        """Valida se tem dados"""
        return len(self.data) > 0


class SimpleValidator(IValidator):
    """Validador simples"""
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate(self, data: List[int]) -> bool:
        """Valida dados"""
        self.errors = []
        
        if not data:
            self.errors.append("Dados vazios")
            return False
        
        for value in data:
            if value < 0:
                self.errors.append(f"Valor negativo: {value}")
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        return self.errors


class DoubleProcessor(IProcessor):
    """Processador que duplica valores"""
    
    def process(self, data: List[int]) -> List[int]:
        """Processa dados duplicando"""
        return [x * 2 for x in data]


class StatisticsAnalyzer(IAnalyzer):
    """Analisador de estatísticas"""
    
    def analyze(self, data: List[int]) -> Dict:
        """Calcula estatísticas"""
        if not data:
            return {}
        
        return {
            'mean': sum(data) / len(data),
            'max': max(data),
            'min': min(data),
            'sum': sum(data),
            'count': len(data)
        }


# ============================================================================
# ORQUESTRADOR - Usa apenas interfaces, não implementações concretas
# ============================================================================

class DataPipeline:
    """Pipeline que usa interfaces para desacoplar"""
    
    def __init__(self, 
                 source: IDataSource,
                 validator: IValidator,
                 processor: IProcessor,
                 analyzer: IAnalyzer):
        # ← Recebe interfaces, não implementações!
        self.source = source
        self.validator = validator
        self.processor = processor
        self.analyzer = analyzer
        self.result = None
    
    def execute(self) -> Dict:
        """Executa pipeline"""
        
        # Ler dados
        data = self.source.read()
        
        if not self.source.is_valid():
            return {'error': 'Dados inválidos'}
        
        # Validar
        if not self.validator.validate(data):
            return {'errors': self.validator.get_errors()}
        
        # Processar
        processed_data = self.processor.process(data)
        
        # Analisar
        self.result = self.analyzer.analyze(processed_data)
        
        return {'success': True, 'result': self.result}
    
    def get_result(self) -> Dict:
        return self.result or {}


# ============================================================================
# USO - Fácil de trocar implementações
# ============================================================================

def main():
    """Exemplo de uso com interfaces"""
    
    # Criar implementações concretas
    source = FileDataSource("dados.txt")
    validator = SimpleValidator()
    processor = DoubleProcessor()
    analyzer = StatisticsAnalyzer()
    
    # Criar pipeline com interfaces
    pipeline = DataPipeline(source, validator, processor, analyzer)
    
    # Executar
    result = pipeline.execute()
    print(f"Resultado: {result}")
    
    # Trocar implementação é trivial!
    # Poderia usar: NumpyProcessor, AdvancedValidator, etc


# ============================================================================
# ANÁLISE ESPERADA
# ============================================================================

"""
ACOPLAMENTOS ESPERADOS (MUITO REDUZIDOS!):

[1] DataPipeline → IDataSource (interface)
    Tipo: Baixo acoplamento
    Motivo: Recebe apenas interface, não implementação
    Benefício: Pode trocar FileDataSource por qualquer outra implementação

[2] DataPipeline → IValidator (interface)
    Tipo: Baixo acoplamento
    Motivo: Recebe apenas interface, não implementação
    Benefício: Pode trocar SimpleValidator por outra implementação

[3] DataPipeline → IProcessor (interface)
    Tipo: Baixo acoplado
    Motivo: Recebe apenas interface, não implementação
    Benefício: Pode trocar DoubleProcessor por outra implementação

[4] DataPipeline → IAnalyzer (interface)
    Tipo: Baixo acoplado
    Motivo: Recebe apenas interface, não implementação
    Benefício: Pode trocar StatisticsAnalyzer por outra implementação

ÍNDICE DE COESÃO ESPERADO: 85-95% (EXCELENTE!)
    Razão: Acoplamento é apenas com interfaces, não implementações
    Benefício: Fácil testar, trocar, estender

PADRÃO: Dependency Injection com Interfaces
    Conceito: Classes recebem dependências (injeção)
             Dependências são interfaces (abstrações)
             Não conhecem implementações concretas

VANTAGENS:
    ✓ Baixo acoplamento
    ✓ Fácil de testar (mock das interfaces)
    ✓ Fácil de estender (novas implementações)
    ✓ Fácil de trocar (implementações intercambiáveis)
    ✓ Segue princípios SOLID
"""
