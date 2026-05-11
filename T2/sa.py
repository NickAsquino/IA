import random     
import math        
import matplotlib.pyplot as plt

def ler_cnf(caminho):
    # 4 -18 19 0 -> 4 é a variável, -18 é a negação da variável 18, 19 é a variável 19, e o 0 indica o fim da cláusula. 
    #Ex: (x4 OR NOT x18 OR x19) AND (x1 OR x2 OR NOT x3) AND ...
    clausulas = [] 
    n_vars = 0     
    # Abre o arquivo em modo de leitura ('r' = read)
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

# aqui para Maximizar o número de cláusulas satisfeitas
def funcao_objetivo(vetor_solucao, clausulas): 
    satisfeitas = 0
    
    for clausula in clausulas: 
        for literal in clausula:
            var = abs(literal) - 1 # Ajuste para índice 0 da lista
            
            # Se a condição da cláusula for atendida...
            if ((literal > 0 and vetor_solucao[var] == 1) or (literal < 0 and vetor_solucao[var] == 0)):
                satisfeitas += 1 
                break
                
    return satisfeitas




def vizinho(s, percentual=0.05):
    novo = s.copy()
    n = len(s)
    qtd = max(1, int(percentual * n)) # Pelo menos 1 bit será alterado
    indices = random.sample(range(n), qtd)
    
    for i in indices:
        novo[i] = 1 - novo[i]
    return novo

def temperatura(it, itMax, t_fator):
    return (1 - (it / itMax)) ** t_fator


# (Adicionei o t_fator=3 como parâmetro para alimentar a fórmula da temperatura)
def simulated_annealing(vetor_solucao, clausulas, T0, alpha, max_iter, SAmax, t_fator=3):
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
            
            # --- SUBSTITUÍDO: Aqui chamamos a função vizinho que inverte 5% ---
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
        # --- SUBSTITUÍDO: Aqui chamamos a função de queda de temperatura do professor ---
        T = temperatura(avaliacoes, max_iter, t_fator)
        
    return melhor_solucao, melhor_fitness, historico_fitness, historico_temperatura

if __name__ == "__main__":
    caminho = "uf20-01.cnf"
    
    try:
        n_vars, clausulas = ler_cnf(caminho)
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho} não foi encontrado. Certifique-se de que ele está na mesma pasta do script.")
        exit()

    print(f"Problema carregado: {n_vars} variáveis e {len(clausulas)} cláusulas.")
    
    vetor_solucao_inicial = [random.randint(0, 1) for _ in range(n_vars)]
    fitness_inicial = funcao_objetivo(vetor_solucao_inicial, clausulas)
    print(f"Cláusulas satisfeitas inicialmente: {fitness_inicial} de {len(clausulas)}")
    
    # Parâmetros
    TEMPERATURA_INICIAL = 1.0 # Inicial ajustada para 1.0 porque a fórmula do professor começa em 1
    ALPHA = 0.95 # Apenas para manter o parâmetro da função, mas o professor usa t_fator
    MAX_ITERACOES = 10000
    SAMAX = 10 
    T_FATOR = 3 # Fator de resfriamento da fórmula do professor
    
    print("\nIniciando Simulated Annealing...")
    
    melhor_sol, melhor_fit, historico, hist_temp = simulated_annealing(
        vetor_solucao_inicial, clausulas, TEMPERATURA_INICIAL, ALPHA, MAX_ITERACOES, SAMAX, T_FATOR
    )
    print(f"\nBusca finalizada!")
    print(f"Melhor quantidade de cláusulas satisfeitas: {melhor_fit} de {len(clausulas)}")
    
    # Plotando o gráfico de evolução do fitness ao longo das iterações
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Eixo Y Esquerdo: Cláusulas satisfeitas (Azul)
    cor_azul = 'blue'
    ax1.set_xlabel("Iteração")
    ax1.set_ylabel("Cláusulas Satisfeitas", color=cor_azul)
    # Usamos linewidth pequeno para formar o bloco denso de exploração igual à imagem
    ax1.plot(historico, color=cor_azul, linewidth=0.5)
    ax1.tick_params(axis='y', labelcolor=cor_azul)

    # Eixo Y Direito: Temperatura (Vermelho)
    ax2 = ax1.twinx() # Cria um segundo eixo Y que partilha o mesmo eixo X
    cor_vermelha = 'red'
    ax2.set_ylabel("Temperatura", color=cor_vermelha)
    # Linha tracejada (linestyle='--') como na sua imagem
    ax2.plot(hist_temp, color=cor_vermelha, linestyle='--', linewidth=1.5)
    ax2.tick_params(axis='y', labelcolor=cor_vermelha)

    # Título do gráfico tal como no exemplo
    plt.title(f"3SAT {n_vars} variáveis, {len(clausulas)} cláusulas")
    
    # Ajusta o layout para evitar que as margens cortem as legendas
    fig.tight_layout() 
    
    # Exibe o gráfico
    plt.show()