# Ant Clustering — Agrupamento de Dados com Formigas

Implementação do algoritmo de agrupamento inspirado no comportamento coletivo de formigas, desenvolvido em C. O projeto foi construído em três etapas progressivas, da versão mais simples até o agrupamento de dados reais com visualização em HTML.

---

## Estrutura do projeto

```
T1/
├── AgruparItens/
│   └── etapa1.c              # Etapa 1: itens homogêneos (sem atributos)
│
├── AgruparDados/
│   ├── etapa2-ab.c           # Etapa 2 (a,b): estrutura do ambiente e distribuição
│   ├── etapa2-c.c            # Etapa 2 (c): estrutura da formiga com item
│   └── etapa2-d.c            # Etapa 2 (d): regras com dissimilaridade euclidiana
│
└── Grupos/
    ├── etapa3.c          # Etapa 3: leitura de arquivo + visualização HTML
    ├── grupo4.txt            # Dados com 4 grupos (400 itens)
    ├── grupo15.txt           # Dados com 15 grupos (600 itens)
    └── resultados/
        ├── teste1.html                        # 4 grupos, k1 = 0.3; k2 = 0.6; α = 11.8029
        ├── teste2.html                        # 4 grupos, k1 = 0.01, k2 = 0.015, α = 30
        ├── teste3.html                        # 4 grupos, k1 = 0.5, k2 = 0.025, α = 0.35
        └── teste4-modificacaoParametros.html  # 15 grupos,k1 = 0.9 e k2 = 0.05, α = 0.11,
```

---

## Pré-requisitos

- Compilador C (GCC recomendado)
- Navegador web (para visualizar os HTMLs gerados)

---

## Como compilar e rodar

### Etapa 1 — Agrupamento de itens homogêneos

```bash
gcc AgruparItens/etapa1.c -o etapa1 -lm
./etapa1
```

### Etapa 2 — Agrupamento de dados com atributos

```bash
gcc AgruparDados/etapa2-d.c -o etapa2 -lm
./etapa2
```

### Etapa 3 — Agrupamento com dados reais + visualização HTML

```bash
gcc Grupos/etapa3.c -o etapa3 -lm
```

Antes de rodar, abra o arquivo `etapa3.c` e ajuste os parâmetros no topo conforme o teste desejado:

```c
#define M          64        // tamanho da matriz
#define NFORMIGAS  100       // quantidade de formigas
#define NITENS     400       // quantidade de itens (deve bater com o arquivo)
#define ALPHA      11.8029   // fator de escala de distância
#define K1         0.3       // facilidade de pegar
#define K2         0.6       // facilidade de largar
```

Depois rode passando o arquivo de dados:

```bash
# Para 4 grupos
./etapa3 grupo4.txt

# Para 15 grupos
./etapa3 grupo15.txt
```

O programa gera automaticamente um arquivo `simulacao.html` na pasta atual.  
Abra esse arquivo em qualquer navegador para ver a animação completa.

---

## Parâmetros testados

| Teste | Arquivo       | Grupos | Formigas | Iterações  | α       | k1   | k2    |
|-------|---------------|--------|----------|------------|---------|------|-------|
| 1     | grupo4.txt    | 4      | 100      | 50.000.000 | 11.8029 | 0.3  | 0.6   |
| 2     | grupo4.txt    | 4      | 100      | 20.000.000 | 30.0    | 0.01 | 0.015 |
| 3     | grupo4.txt    | 4      | 15       | 20.000.000 | 0.35    | 0.5  | 0.025 |
| 4     | grupo15.txt   | 15     | 15       | 50.000.000 | 0.11    | 0.9  | 0.05  |

> **Nota:** Os arquivos HTML prontos na pasta `resultados/` foram gerados com esses parâmetros e podem ser abertos diretamente sem precisar recompilar.

---

## Visualização HTML

O player gerado permite:

- **▶ Play / ⏸ Pause** — animar a simulação automaticamente
- **◀ / ▶** — navegar frame a frame
- **Slider** — pular para qualquer ponto da simulação
- Cada grupo aparece em uma cor diferente
- Formigas livres aparecem em cinza, formigas carregando em branco

---

## Como o algoritmo funciona (resumo)

Cada formiga caminha aleatoriamente pela grade. Ao encontrar um item, calcula a similaridade desse item com os vizinhos da célula atual. Se o item estiver isolado (baixa similaridade), a formiga tende a pegá-lo. Se estiver carregando um item e encontrar uma região com muitos itens similares, tende a largá-lo ali. Com muitas iterações, esse comportamento simples produz o agrupamento espontâneo dos dados.
