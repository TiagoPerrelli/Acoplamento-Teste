#!/usr/bin/env python3

import os
import sys
import numpy as np

from extrator_codigo import ExtratorCodigo
from analisador_zhang import AnalisadorZhang, gerar_html_zhang
from analisador_dou import AnalisadorDou, gerar_html_dou


def solicitar_probabilidades(funcoes_ordenadas):
    """Solicita ao usuário as probabilidades de mudança de cada função"""
    print("\n" + "="*70)
    print("📊 DEFINA A PROBABILIDADE DE MUDANÇA DAS FUNÇÕES (Zhang)")
    print("="*70)
    print("\nDigite o índice da função e sua probabilidade (0 a 1), separados por vírgula.")
    print("Exemplo: 1, 0.3  (função [1] tem probabilidade 0.3)")
    print("Deixe em branco para usar padrão 0.5 para todas.")
    print("\nFunções encontradas:\n")

    for idx, funcao in enumerate(funcoes_ordenadas, 1):
        nome_curto = funcao.split('.')[-1]
        arquivo = funcao.split('.')[0]
        print(f"[{idx}] {nome_curto:30} ({arquivo})")

    probabilidades = {funcao: 0.5 for funcao in funcoes_ordenadas}

    print("\n" + "-"*70)
    print("Digite as probabilidades (ou Enter para padrão 0.5):")
    print("Digite 'pronto' ou Enter vazio quando terminar.")
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
                print(f"❌ Índice inválido! Use 1 a {len(funcoes_ordenadas)}")
                continue

            if prob < 0 or prob > 1:
                print("❌ Probabilidade inválida! Use valores entre 0 e 1")
                continue

            funcao = funcoes_ordenadas[idx - 1]
            probabilidades[funcao] = prob
            print(f"✅ [{idx}] = {prob}")

        except (ValueError, IndexError):
            print("❌ Formato inválido! Use: número, valor")

    print("\n" + "="*70)
    print("📋 PROBABILIDADES DEFINIDAS:")
    print("="*70)
    for idx, funcao in enumerate(funcoes_ordenadas, 1):
        nome_curto = funcao.split('.')[-1]
        prob = probabilidades[funcao]
        print(f"[{idx}] {nome_curto:30} → {prob:.1%}")
    print("="*70 + "\n")

    return probabilidades


def solicitar_manual_coefficients(variaveis_ordenadas):
    """Solicita ao usuário os Manual Coefficients de cada variável"""
    print("\n" + "="*70)
    print("📊 DEFINA O MANUAL COEFFICIENT DAS VARIÁVEIS (Dou)")
    print("="*70)
    print("\nDigite o índice da variável e seu MC (> 0), separados por vírgula.")
    print("Exemplo: 1, 1.5  (variável [1] tem MC = 1.5)")
    print("Deixe em branco para usar padrão 1.0 para todas.")
    print("\nVariáveis encontradas:\n")

    for idx, var in enumerate(variaveis_ordenadas, 1):
        var_nome = var.split("::")[-1]
        funcao = var.split("::")[0].split(".")[-1]
        print(f"[{idx}] {var_nome:30} (em {funcao})")

    manual_coefficients = {var: 1.0 for var in variaveis_ordenadas}

    print("\n" + "-"*70)
    print("Digite os Manual Coefficients (ou Enter para padrão 1.0):")
    print("Digite 'pronto' ou Enter vazio quando terminar.")
    print("-"*70 + "\n")

    while True:
        entrada = input(">>> ").strip()

        if entrada == "" or entrada.lower() == "pronto":
            break

        try:
            partes = entrada.split(',')
            idx = int(partes[0].strip())
            mc = float(partes[1].strip())

            if idx < 1 or idx > len(variaveis_ordenadas):
                print(f"❌ Índice inválido! Use 1 a {len(variaveis_ordenadas)}")
                continue

            if mc <= 0:
                print("❌ MC inválido! Use valores maiores que 0")
                continue

            var = variaveis_ordenadas[idx - 1]
            manual_coefficients[var] = mc
            print(f"✅ [{idx}] = {mc}")

        except (ValueError, IndexError):
            print("❌ Formato inválido! Use: número, valor")

    print("\n" + "="*70)
    print("📋 MANUAL COEFFICIENTS DEFINIDOS:")
    print("="*70)
    for idx, var in enumerate(variaveis_ordenadas, 1):
        var_nome = var.split("::")[-1]
        mc = manual_coefficients[var]
        print(f"[{idx}] {var_nome:30} → {mc:.2f}")
    print("="*70 + "\n")

    return manual_coefficients


def obter_matriz_adjacencia(funcoes_ordenadas, chamadas):
    """Gera matriz de adjacência de chamadas entre funções"""
    n = len(funcoes_ordenadas)
    matriz = np.zeros((n, n))

    indice_map = {f: i for i, f in enumerate(funcoes_ordenadas)}

    for origem, destinos in chamadas.items():
        if origem in indice_map:
            i = indice_map[origem]
            for destino in destinos:
                if destino in indice_map:
                    j = indice_map[destino]
                    matriz[i][j] += 1

    return matriz


def mostrar_ajuda():
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║        📊 ANALISADOR DE ACOPLAMENTO - DUAS METODOLOGIAS              ║
║    Zhang et al. (2011) + Dou et al. (2023) [VRM Model]               ║
╚════════════════════════════════════════════════════════════════════════╝

MODO DE USO:

  1. Análise rápida (valores padrão):
     python main.py ./seu_projeto

  2. Com probabilidades personalizadas (Zhang):
     python main.py ./seu_projeto -p

  3. Com Manual Coefficients personalizados (Dou):
     python main.py ./seu_projeto -dou

  4. Ambos personalizados:
     python main.py ./seu_projeto -p -dou

FLAGS:
  -p      Ativa modo interativo para probabilidades (Zhang)
  -dou    Ativa modo interativo para Manual Coefficients (Dou)
  -h      Exibe esta mensagem de ajuda

SAÍDA:
  Gera 2 relatórios HTML:
  - report/analise_automatica_zhang.html (funções)
  - report/analise_automatica_dou.html (variáveis + árvore de dependências)

═══════════════════════════════════════════════════════════════════════════
    """)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        mostrar_ajuda()
        sys.exit(0)

    pasta_projeto = sys.argv[1]
    modo_interativo_zhang = '-p' in sys.argv
    modo_interativo_dou = '-dou' in sys.argv

    if not os.path.isdir(pasta_projeto):
        print(f"❌ Pasta '{pasta_projeto}' não encontrada!")
        sys.exit(1)

    print(f"\n📊 Analisando projeto em: {pasta_projeto}\n")

    # Extrair código
    extrator = ExtratorCodigo(pasta_projeto)

    if not extrator.funcoes:
        print("❌ Nenhuma função encontrada!")
        sys.exit(1)

    if not extrator.variaveis:
        print("❌ Nenhuma variável encontrada!")
        sys.exit(1)

    # ========================================================================
    # METODOLOGIA 1: ZHANG ET AL. (FUNÇÕES)
    # ========================================================================

    funcoes_ordenadas = sorted(extrator.funcoes.keys())

    if modo_interativo_zhang:
        probabilidades = solicitar_probabilidades(funcoes_ordenadas)
    else:
        probabilidades = {funcao: 0.5 for funcao in funcoes_ordenadas}
        print(f"📊 Usando probabilidade padrão 0.5 para {len(funcoes_ordenadas)} funções (Zhang)\n")

    print(f"📊 Analisando chamadas entre funções...")
    matriz = obter_matriz_adjacencia(funcoes_ordenadas, extrator.chamadas)

    print("📊 Calculando métricas Zhang et al. (2011)...\n")
    analise_zhang = AnalisadorZhang(funcoes_ordenadas, matriz, probabilidades)

    # ========================================================================
    # METODOLOGIA 2: DOU ET AL. (VARIÁVEIS)
    # ========================================================================

    variaveis_ordenadas = sorted(extrator.variaveis.keys())

    if modo_interativo_dou:
        manual_coefficients = solicitar_manual_coefficients(variaveis_ordenadas)
    else:
        manual_coefficients = {var: 1.0 for var in variaveis_ordenadas}
        print(f"📊 Usando MC padrão 1.0 para {len(variaveis_ordenadas)} variáveis (Dou)\n")

    print("📊 Calculando métricas Dou et al. (2023)...\n")
    analise_dou = AnalisadorDou(
        extrator.variaveis, 
        manual_coefficients, 
        extrator.var_dependencies
    )

    # ========================================================================
    # GERAR RELATÓRIOS HTML
    # ========================================================================

    if not os.path.exists("report"):
        os.makedirs("report")

    # Relatório Zhang
    html_zhang = gerar_html_zhang(funcoes_ordenadas, analise_zhang)
    with open("report/analise_automatica_zhang.html", "w", encoding="utf-8") as f:
        f.write(html_zhang)

    # Relatório Dou
    html_dou = gerar_html_dou(variaveis_ordenadas, analise_dou)
    with open("report/analise_automatica_dou.html", "w", encoding="utf-8") as f:
        f.write(html_dou)

    # ========================================================================
    # EXIBIR RESULTADOS
    # ========================================================================

    print(f"✅ Análise concluída!\n")
    print(f"{'='*70}")
    print(f"📊 RESULTADOS COMPARATIVOS")
    print(f"{'='*70}\n")

    print(f"METODOLOGIA 1: Zhang et al. (2011) - Análise de FUNÇÕES")
    print(f"  Entropy (H):              {analise_zhang.H_entropy:.4f}")
    print(f"  Classificação:            {analise_zhang.classificacao_acoplamento()}\n")

    print(f"METODOLOGIA 2: Dou et al. (2023) - VRM Model (VARIÁVEIS)")
    print(f"  Acoplamento Total (C):    {analise_dou.C_vrm:.4f}")
    print(f"  HC Médio:                 {analise_dou.HC_medio:.4f}")
    print(f"  SC Médio:                 {analise_dou.SC_medio:.4f}")

    print(f"{'='*70}")
    print(f"📄 Relatórios HTML gerados:\n")
    print(f"  1. report/analise_automatica_zhang.html")
    print(f"  2. report/analise_automatica_dou.html")
    print(f"\n💡 Abra os relatórios no navegador!\n")


if __name__ == "__main__":
    main()
