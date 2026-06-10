import random
import math
import matplotlib.pyplot as plt
import os
import statistics

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

# Ti = T0 * (Tn/T0)^(i/N)
def temperatura_schedule1(T0, Tn, i, N):
    if i >= N:
        return Tn
    return T0 * ((Tn / T0) ** (i / N))

def simulated_annealing(vetor_solucao, clausulas, T0, Tn, alpha, max_iter, SAmax, rotina):
    T = T0
    solucao_atual = vetor_solucao[:]
    fitness_atual = funcao_objetivo(solucao_atual, clausulas)
    
    melhor_solucao = solucao_atual[:]
    melhor_fitness = fitness_atual
    
    historico_fitness = []
    historico_temperatura = []
    avaliacoes = 0 
    
    while T > Tn and avaliacoes < max_iter:
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

        # Atualiza temperatura conforme a rotina escolhida
        if rotina == "geometrica":
            T = T * alpha
        else:  # schedule1
            T = temperatura_schedule1(T0, Tn, avaliacoes, max_iter)
        
    return melhor_solucao, melhor_fitness, historico_fitness, historico_temperatura


if __name__ == "__main__":
    arquivos = [
        "teste1/uf20-01.cnf",
        "teste2/uf100-01.cnf",
        "teste3/uf250-01.cnf"
    ]
    arquivo_log = "resultados.txt"
    numero_execucoes = 10

    TEMPERATURA_INICIAL = 50.0
    TEMPERATURA_FINAL = 0.0001
    ALPHA = 0.95
    MAX_ITERACOES = 10000

    # ← Os dois valores de SAmax e as duas rotinas
    samax_valores = [1, 10]
    rotinas = ["geometrica", "schedule1"]

    with open(arquivo_log, 'w', encoding='utf-8') as f_log:

        for caminho in arquivos:
            try:
                n_vars, clausulas = ler_cnf(caminho)
            except FileNotFoundError:
                print(f"Arquivo {caminho} não encontrado, pulando...")
                continue

            pasta = os.path.dirname(caminho)
            if pasta == "":
                pasta = "."
            nome_arquivo = os.path.basename(caminho).replace(".cnf", "")

            msg_arquivo = f"\n{'='*50}\nArquivo: {caminho}\nProblema: {n_vars} variáveis, {len(clausulas)} cláusulas\n"
            print(msg_arquivo)
            f_log.write(msg_arquivo + "\n")

            # Guarda resultados de todas as configurações para o box-plot combinado
            resultados_por_config = {}
            labels_boxplot = []

            for samax in samax_valores:
                for rotina in rotinas:

                    nome_config = f"{rotina}_samax{samax}"
                    label = f"{'Geom.' if rotina == 'geometrica' else 'Sched1'}\nSAmax={samax}"
                    labels_boxplot.append(label)
                    resultados_por_config[nome_config] = []

                    msg_config = (
                        f"\n--- Configuração: Rotina={rotina} | SAmax={samax} ---\n"
                        f"Iniciando {numero_execucoes} execuções...\n"
                    )
                    print(msg_config)
                    f_log.write(msg_config + "\n")

                    melhor_historico = None
                    melhor_fitness_geral = -1

                    for execucao in range(1, numero_execucoes + 1):
                        vetor_solucao_inicial = [random.randint(0, 1) for _ in range(n_vars)]
                        fitness_inicial = funcao_objetivo(vetor_solucao_inicial, clausulas)

                        msg_exec = f"  Execução {execucao} | inicial: {fitness_inicial} de {len(clausulas)}"
                        print(msg_exec)
                        f_log.write(msg_exec + "\n")

                        melhor_sol, melhor_fit, historico, hist_temp = simulated_annealing(
                            vetor_solucao_inicial, clausulas,
                            TEMPERATURA_INICIAL, TEMPERATURA_FINAL,
                            ALPHA, MAX_ITERACOES, samax, rotina
                        )

                        resultados_por_config[nome_config].append(melhor_fit)

                        # Guarda histórico da melhor execução para o gráfico de convergência
                        if melhor_fit > melhor_fitness_geral:
                            melhor_fitness_geral = melhor_fit
                            melhor_historico = (historico, hist_temp, execucao)

                        msg_fit = f"  Melhor: {melhor_fit} de {len(clausulas)}"
                        print(msg_fit)
                        f_log.write(msg_fit + "\n")

                    # Estatísticas da configuração
                    resultados = resultados_por_config[nome_config]
                    media = statistics.mean(resultados)
                    desvio = statistics.stdev(resultados)

                    msg_stats = (
                        f"\n  >> Resultados: {resultados}\n"
                        f"  >> Média: {media:.2f} | Desvio Padrão: {desvio:.2f}\n"
                        f"  >> Melhor: {max(resultados)} | Pior: {min(resultados)}\n"
                    )
                    print(msg_stats)
                    f_log.write(msg_stats + "\n")

                    # Gráfico de convergência da melhor execução desta configuração
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

            # Box-plot combinado com as 4 configurações — gerado UMA VEZ por instância
            fig, ax = plt.subplots(figsize=(10, 6))

            dados = list(resultados_por_config.values())
            cores = ['#AED6F1', '#2E86C1', '#A9DFBF', '#1E8449']

            bp = ax.boxplot(dados, tick_labels=labels_boxplot, patch_artist=True)
            for patch, cor in zip(bp['boxes'], cores):
                patch.set_facecolor(cor)

            ax.set_ylabel("Cláusulas Satisfeitas")
            ax.set_title(f"Box-plot Comparativo — {nome_arquivo} ({n_vars} vars, {len(clausulas)} cláusulas)")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            fig.tight_layout()

            plt.savefig(os.path.join(pasta, f"boxplot_comparativo_{nome_arquivo}.png"))
            plt.close(fig)
            print(f"Box-plot comparativo salvo para {nome_arquivo}\n")

    print("Todas as execuções concluídas!")
    print(f"Resultados salvos em '{arquivo_log}'.")
    print(f"Os gráficos de convergência e os Box-Plots foram salvos nas respectivas pastas.")
