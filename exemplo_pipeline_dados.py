"""
EXEMPLO 2: Sistema de Processamento de Dados
=============================================

Um exemplo mais complexo com classes e métodos interdependentes
para demonstrar a detecção automática de acoplamentos.
"""

# ============================================================================
# CLASSES E MÉTODOS - Sistema de Processamento de Dados
# ============================================================================

class DataReader:
    """Responsável por ler dados de uma fonte"""
    
    def __init__(self, filename):
        self.filename = filename
        self.data = []
    
    def read_file(self):
        """Lê arquivo e armazena dados"""
        # Simulação: em produção, leria de verdade
        self.data = [10, 20, 30, 40, 50]
        return self.data
    
    def get_data(self):
        """Retorna dados lidos"""
        return self.data
    
    def validate_data(self):
        """Valida se dados foram lidos"""
        return len(self.data) > 0


class DataValidator:
    """Responsável por validar dados"""
    
    def __init__(self, reader):
        self.reader = reader  # ← ACOPLAMENTO: depende de DataReader
        self.errors = []
    
    def validate(self):
        """Valida dados usando reader"""
        if not self.reader.validate_data():  # ← Chama método de reader
            self.errors.append("Dados vazios")
            return False
        
        data = self.reader.get_data()  # ← Obtém dados de reader
        
        for value in data:
            if value < 0:
                self.errors.append(f"Valor negativo: {value}")
        
        return len(self.errors) == 0
    
    def get_errors(self):
        """Retorna lista de erros"""
        return self.errors


class DataProcessor:
    """Responsável por processar dados"""
    
    def __init__(self, reader, validator):
        self.reader = reader          # ← ACOPLAMENTO: depende de DataReader
        self.validator = validator    # ← ACOPLAMENTO: depende de DataValidator
        self.processed_data = []
    
    def process(self):
        """Processa dados após validação"""
        if not self.validator.validate():  # ← Chama validador
            return False
        
        data = self.reader.get_data()  # ← Obtém dados de reader
        self.processed_data = [x * 2 for x in data]  # ← Transforma
        return True
    
    def get_processed_data(self):
        """Retorna dados processados"""
        return self.processed_data


class DataAnalyzer:
    """Responsável por analisar dados processados"""
    
    def __init__(self, processor):
        self.processor = processor  # ← ACOPLAMENTO: depende de DataProcessor
        self.statistics = {}
    
    def analyze(self):
        """Analisa dados processados"""
        data = self.processor.get_processed_data()  # ← Obtém de processor
        
        if not data:
            return False
        
        self.statistics['mean'] = sum(data) / len(data)
        self.statistics['max'] = max(data)
        self.statistics['min'] = min(data)
        self.statistics['sum'] = sum(data)
        
        return True
    
    def get_statistics(self):
        """Retorna estatísticas calculadas"""
        return self.statistics


class ReportGenerator:
    """Responsável por gerar relatório final"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer  # ← ACOPLAMENTO: depende de DataAnalyzer
        self.report = ""
    
    def generate(self):
        """Gera relatório com análise"""
        if not self.analyzer.analyze():  # ← Chama analyzer
            self.report = "Análise falhou"
            return False
        
        stats = self.analyzer.get_statistics()  # ← Obtém estatísticas
        
        self.report = f"""
        ==================== RELATÓRIO ====================
        Média: {stats['mean']:.2f}
        Máximo: {stats['max']:.2f}
        Mínimo: {stats['min']:.2f}
        Total: {stats['sum']:.2f}
        ====================================================
        """
        return True
    
    def print_report(self):
        """Imprime relatório"""
        print(self.report)


# ============================================================================
# FLUXO DE EXECUÇÃO - Demonstração do Sistema
# ============================================================================

def main():
    """Função principal que orquestra o sistema"""
    
    # Criar leitor
    reader = DataReader("dados.txt")
    reader.read_file()
    
    # Criar validador
    validator = DataValidator(reader)
    
    # Criar processador
    processor = DataProcessor(reader, validator)
    
    # Criar analisador
    analyzer = DataAnalyzer(processor)
    
    # Criar gerador de relatório
    report = ReportGenerator(analyzer)
    
    # Executar pipeline
    if report.generate():  # ← Chama generate, que chama analyzer
        report.print_report()
    else:
        print("Erro ao gerar relatório")


if __name__ == "__main__":
    main()


# ============================================================================
# ANÁLISE ESPERADA (O que o analisador automático vai encontrar)
# ============================================================================

"""
ACOPLAMENTOS ESPERADOS:

[1] DataValidator → DataReader
    Tipo: HYBRID DATA-CONTROL
    Motivo: DataValidator chama métodos de DataReader e usa dados

[2] DataProcessor → DataReader
    Tipo: HYBRID DATA-CONTROL
    Motivo: DataProcessor obtém dados de DataReader

[3] DataProcessor → DataValidator
    Tipo: HYBRID DATA-CONTROL
    Motivo: DataProcessor chama validate() de DataValidator

[4] DataAnalyzer → DataProcessor
    Tipo: HYBRID DATA-CONTROL
    Motivo: DataAnalyzer obtém dados processados de DataProcessor

[5] ReportGenerator → DataAnalyzer
    Tipo: HYBRID DATA-CONTROL
    Motivo: ReportGenerator chama analyze() e get_statistics()

[6] main → DataReader
    Tipo: CONTROL
    Motivo: main() cria e chama DataReader

[7] main → DataValidator
    Tipo: CONTROL
    Motivo: main() cria DataValidator

[8] main → DataProcessor
    Tipo: CONTROL
    Motivo: main() cria DataProcessor

[9] main → DataAnalyzer
    Tipo: CONTROL
    Motivo: main() cria DataAnalyzer

[10] main → ReportGenerator
    Tipo: CONTROL
    Motivo: main() cria ReportGenerator

PADRÃO DETECTADO: Pipeline Linear (Chain of Responsibility)
    Reader → Validator → Processor → Analyzer → ReportGenerator
    
    Cada classe é acoplada à anterior, formando uma cadeia.
    Este é um padrão CONHECIDO e JUSTIFICÁVEL!

ÍNDICE DE COESÃO ESPERADO: 30-40% (baixo)
    Razão: Alta interdependência entre classes
    Porém: Acoplamento é NECESSÁRIO para fluxo de dados

RECOMENDAÇÃO: Este padrão é aceitável para pipelines de processamento
    Alternativa: Usar interfaces/protocolos para desacoplar
"""
