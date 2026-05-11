import random     
import math        
import matplotlib.pyplot as plt
import os

def ler_cnf(caminho):
    # 4 -18 19 0 -> 4 é a variável, -18 é a negação da variável 18, 19 é a variável 19, e o 0 indica o fim da cláusula. 
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

def temperatura(it, itMax, t_fator):
    return (1 - (it / itMax)) ** t_fator

def simulated_annealing(vetor_solucao, clausulas, T0, alpha, max_iter, SAmax):
    T = T0
    solucao_atual = vetor_solucao[:]
    fitness_atual = funcao_objetivo(solucao_atual, clausulas)
    
    melhor_solucao = solucao_atual[:]
    melhor_fitness = fitness_atual
    
    historico_fitness = []
    historico_temperatura = []
    avaliacoes = 0 
    
    while T > 0.0001 and avaliacoes < max_iter:
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
            
        T = T * alpha;
        
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
    ALPHA = 0.95
    MAX_ITERACOES = 10000
    SAMAX = 10

    with open(arquivo_log, 'w', encoding='utf-8') as f_log:

        for caminho in arquivos:
            try:
                n_vars, clausulas = ler_cnf(caminho)
            except FileNotFoundError:
                print(f"Arquivo {caminho} não encontrado, pulando...")
                continue

            msg_inicio = f"\n{'='*50}\nArquivo: {caminho}\nProblema carregado: {n_vars} variáveis e {len(clausulas)} cláusulas.\nIniciando as {numero_execucoes} execuções...\n"
            print(msg_inicio)
            f_log.write(msg_inicio + "\n")

            for execucao in range(1, numero_execucoes + 1):
                vetor_solucao_inicial = [random.randint(0, 1) for _ in range(n_vars)]
                fitness_inicial = funcao_objetivo(vetor_solucao_inicial, clausulas)

                msg_exec = f"--- Execução {execucao} ---"
                msg_fit_ini = f"Cláusulas satisfeitas inicialmente: {fitness_inicial} de {len(clausulas)}"

                print(msg_exec)
                print(msg_fit_ini)
                f_log.write(f"{msg_exec}\n{msg_fit_ini}\n")

                melhor_sol, melhor_fit, historico, hist_temp = simulated_annealing(
                    vetor_solucao_inicial, clausulas, TEMPERATURA_INICIAL, ALPHA, MAX_ITERACOES, SAMAX
                )

                msg_fit_fim = f"Melhor quantidade de cláusulas satisfeitas: {melhor_fit} de {len(clausulas)}\n"
                print(msg_fit_fim)
                f_log.write(f"{msg_fit_fim}\n")

                fig, ax1 = plt.subplots(figsize=(8, 6))

                cor_azul = 'blue'
                ax1.set_xlabel("Iteração")
                ax1.set_ylabel("Cláusulas Satisfeitas", color=cor_azul)
                ax1.plot(historico, color=cor_azul, linewidth=0.5)
                ax1.tick_params(axis='y', labelcolor=cor_azul)

                ax2 = ax1.twinx()
                cor_vermelha = 'red'
                ax2.set_ylabel("Temperatura", color=cor_vermelha)
                ax2.plot(hist_temp, color=cor_vermelha, linestyle='--', linewidth=1.5)
                ax2.tick_params(axis='y', labelcolor=cor_vermelha)

                # Nome do arquivo inclui qual instância é pra não sobrescrever
                pasta = os.path.dirname(caminho)
                nome_arquivo = os.path.basename(caminho).replace(".cnf", "")

                # nome_base = caminho.replace(".cnf", "")

                plt.title(f"Execução {execucao} - {nome_arquivo} - {n_vars} vars, {len(clausulas)} cláusulas")
                fig.tight_layout()

                nome_grafico = os.path.join(pasta, f"grafico_{nome_arquivo}_exec{execucao}.png")
                # nome_grafico = f"grafico_{nome_arquivo}_exec{execucao}.png"
                plt.savefig(nome_grafico)
                plt.close(fig)

    print(f"Todas as execuções concluídas!")
    print(f"Resultados salvos em '{arquivo_log}'.")
    print(f"Os 10 gráficos foram salvos na mesma pasta do script (formato PNG).")