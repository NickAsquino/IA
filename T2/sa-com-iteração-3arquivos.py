import random     
import math        
import matplotlib.pyplot as plt
import os
import numpy as np

def ler_cnf(caminho):
    clausulas = [] 
    n_vars = 0     
    with open(caminho, 'r') as f:
        for linha in f:
            linha = linha.strip() 
            if (linha == '' or 
                linha.startswith('c') or 
                linha.startswith('%') or 
                linha.startswith('0')):
                continue
            if linha.startswith('p'):
                partes = linha.split()
                n_vars = int(partes[2]) 
            else:
                try:
                    clausula = list(map(int, linha.split()))
                    clausula = [x for x in clausula if x != 0]
                    clausulas.append(clausula)
                except ValueError:
                    continue 
    return n_vars, clausulas

def funcao_objetivo(vetor_solucao, clausulas): 
    satisfeitas = 0
    for clausula in clausulas: 
        for literal in clausula:
            var = abs(literal) - 1
            if ((literal > 0 and vetor_solucao[var] == 1) or (literal < 0 and vetor_solucao[var] == 0)):
                satisfeitas += 1 
                break
    return satisfeitas

def vizinho(s, percentual=0.05):
    novo = s.copy()
    n = len(s)
    qtd = max(1, int(percentual * n)) 
    indices = random.sample(range(n), qtd)
    for i in indices:
        novo[i] = 1 - novo[i]
    return novo

def calcular_temperatura(rotina, T0, T_final, avaliacao_atual, max_iter, T_atual, alpha):
    if rotina == "geometrica":
        return T_atual * alpha
    elif rotina == "schedule1":
        # Ti = T0 * (T_final/T0)^(i/N)
        return T0 * (T_final / T0) ** (avaliacao_atual / max_iter)

def simulated_annealing(vetor_solucao, clausulas, T0, alpha, max_iter, SAmax, rotina):
    T_final = 0.0001
    T = T0
    solucao_atual = vetor_solucao[:]
    fitness_atual = funcao_objetivo(solucao_atual, clausulas)
    
    melhor_solucao = solucao_atual[:]
    melhor_fitness = fitness_atual
    
    historico_fitness = []
    historico_temperatura = []
    avaliacoes = 0 
    
    while T > T_final and avaliacoes < max_iter:
        IterT = 0 
        while IterT < SAmax and avaliacoes < max_iter:
            IterT += 1
            avaliacoes += 1
            
            nova_solucao = vizinho(solucao_atual, percentual=0.05)
            nova_fitness = funcao_objetivo(nova_solucao, clausulas)
            delta = nova_fitness - fitness_atual
            
            if delta > 0:
                solucao_atual = nova_solucao
                fitness_atual = nova_fitness
                if fitness_atual > melhor_fitness:
                    melhor_solucao = solucao_atual[:]
                    melhor_fitness = fitness_atual
            else:
                probabilidade = math.exp(delta / T)
                if random.random() < probabilidade:
                    solucao_atual = nova_solucao
                    fitness_atual = nova_fitness
            
            historico_fitness.append(fitness_atual)
            historico_temperatura.append(T)

        # Atualiza temperatura APÓS o ciclo SAmax
        T = calcular_temperatura(rotina, T0, T_final, avaliacoes, max_iter, T, alpha)
        
    return melhor_solucao, melhor_fitness, historico_fitness, historico_temperatura


if __name__ == "__main__":
    arquivos = [
        "T2/teste1/uf20-01.cnf",
        "T2/teste2/uf100-01.cnf",
        "T2/teste3/uf250-01.cnf"
    ]
    arquivo_log = "resultados.txt"
    numero_execucoes = 10

    TEMPERATURA_INICIAL = 50.0
    T_FINAL = 0.0001
    ALPHA = 0.95
    MAX_ITERACOES = 10000

    rotinas = ["geometrica", "schedule1"]
    samax_valores = [1, 10]

    with open(arquivo_log, 'w', encoding='utf-8') as f_log:

        for caminho in arquivos:
            try:
                n_vars, clausulas = ler_cnf(caminho)
            except FileNotFoundError:
                print(f"Arquivo {caminho} não encontrado, pulando...")
                continue

            pasta = os.path.dirname(caminho)
            nome_arquivo = os.path.basename(caminho).replace(".cnf", "")

            # Guarda resultados de TODAS as configurações desta instância
            resultados_por_config = {}

            for samax in samax_valores:
                for rotina in rotinas:

                    nome_config = f"{rotina}_samax{samax}"
                    resultados_por_config[nome_config] = []

                    msg_inicio = (
                        f"\n{'='*50}\n"
                        f"Arquivo: {caminho} | Rotina: {rotina} | SAmax: {samax}\n"
                        f"Problema: {n_vars} variáveis, {len(clausulas)} cláusulas\n"
                    )
                    print(msg_inicio)
                    f_log.write(msg_inicio + "\n")

                    melhor_historico = None
                    melhor_fitness_geral = -1

                    for execucao in range(1, numero_execucoes + 1):
                        vetor_solucao_inicial = [random.randint(0, 1) for _ in range(n_vars)]
                        fitness_inicial = funcao_objetivo(vetor_solucao_inicial, clausulas)

                        msg_exec = f"--- Execução {execucao} | {nome_config} ---"
                        msg_fit_ini = f"Cláusulas satisfeitas inicialmente: {fitness_inicial} de {len(clausulas)}"
                        print(msg_exec)
                        f_log.write(f"{msg_exec}\n{msg_fit_ini}\n")

                        melhor_sol, melhor_fit, historico, hist_temp = simulated_annealing(
                            vetor_solucao_inicial, clausulas,
                            TEMPERATURA_INICIAL, ALPHA, MAX_ITERACOES, samax, rotina
                        )

                        # Guarda resultado desta execução
                        resultados_por_config[nome_config].append(melhor_fit)

                        if melhor_fit > melhor_fitness_geral:
                            melhor_fitness_geral = melhor_fit
                            melhor_historico = (historico, hist_temp, execucao)

                        msg_fit_fim = f"Melhor resultado: {melhor_fit} de {len(clausulas)}\n"
                        print(msg_fit_fim)
                        f_log.write(f"{msg_fit_fim}\n")

                    # Estatísticas
                    resultados = resultados_por_config[nome_config]
                    media = sum(resultados) / len(resultados)
                    desvio = (sum((x - media)**2 for x in resultados) / len(resultados)) ** 0.5

                    msg_stats = (
                        f"\n>> {nome_config}\n"
                        f"   Média: {media:.2f} | Desvio: {desvio:.2f}\n"
                        f"   Melhor: {max(resultados)} | Pior: {min(resultados)}\n"
                    )
                    print(msg_stats)
                    f_log.write(msg_stats + "\n")

                    # Gráfico de convergência (melhor execução)
                    hist, hist_t, exec_num = melhor_historico
                    fig, ax1 = plt.subplots(figsize=(8, 6))
                    ax1.set_xlabel("Iteração")
                    ax1.set_ylabel("Cláusulas Satisfeitas", color='blue')
                    ax1.plot(hist, color='blue', linewidth=0.5)
                    ax1.tick_params(axis='y', labelcolor='blue')
                    ax2 = ax1.twinx()
                    ax2.set_ylabel("Temperatura", color='red')
                    ax2.plot(hist_t, color='red', linestyle='--', linewidth=1.5)
                    ax2.tick_params(axis='y', labelcolor='red')
                    plt.title(f"Convergência - {nome_arquivo} | {rotina} | SAmax={samax} | Exec {exec_num}")
                    fig.tight_layout()
                    plt.savefig(os.path.join(pasta, f"grafico_{nome_arquivo}_{nome_config}.png"))
                    plt.close(fig)

            # ── Box-plot combinado com as 4 configurações lado a lado ──────────
            # Gerado UMA VEZ por instância, após rodar todas as 4 configurações
            fig, ax = plt.subplots(figsize=(10, 6))

            dados = list(resultados_por_config.values())
            labels = [
                "Geom.\nSAmax=1",
                "Geom.\nSAmax=10",
                "Sched1\nSAmax=1",
                "Sched1\nSAmax=10"
            ]

            bp = ax.boxplot(dados, tick_labels=labels, patch_artist=True)

            # Cores diferentes para cada configuração
            cores = ['#AED6F1', '#2E86C1', '#A9DFBF', '#1E8449']
            for patch, cor in zip(bp['boxes'], cores):
                patch.set_facecolor(cor)

            ax.set_ylabel("Cláusulas Satisfeitas")
            ax.set_title(f"Box-plot Comparativo — {nome_arquivo} ({n_vars} vars, {len(clausulas)} cláusulas)")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            fig.tight_layout()

            plt.savefig(os.path.join(pasta, f"boxplot_comparativo_{nome_arquivo}.png"))
            plt.close(fig)
            print(f"Box-plot comparativo salvo para {nome_arquivo}")

    print("Todas as execuções concluídas!")
    print(f"Resultados salvos em '{arquivo_log}'.")
    print(f"Os 10 gráficos foram salvos na mesma pasta do script (formato PNG).")