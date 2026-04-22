#include <stdio.h>
#include <stdlib.h>

#define M 50
#define NFORMIGAS 15
#define RAIO 1
#define NITENS 1000

typedef struct {
    int ocupado;
    double x;
    double y;
} Item;

Item ambiente[M][M];

typedef struct {
    int linha;
    int col;
    int carregando; // 0 ou 1
} Formiga;

Formiga formigas[NFORMIGAS];

void inicializar();
void imprimir();
void mudar(int f);
int qtdItensVizinhanca(int linha, int col);
void tentarPegar(int f);
void tentarLargar(int f);
void simular(int passos);

int main(void)
{
    inicializar();

    printf("*-*-*-*- Passo 1 -*-*-*-*\n");
    imprimir();

    // 50 em 50
    simular(100000);

    printf("\n*-*-*-*- Passo final -*-*-*-*\n");
    imprimir();

    return 0;
}

void inicializar()
{
    int i, j;

    for (i = 0; i < M; i++) {
        for (j = 0; j < M; j++) {
            ambiente[i][j].ocupado = 0;
            ambiente[i][j].x = 0.0;
            ambiente[i][j].y = 0.0;
        }
    }

    int itens = NITENS;

    while (itens > 0) {
        i = rand() % M;
        j = rand() % M;
        if (ambiente[i][j].ocupado == 0) {
            ambiente[i][j].ocupado = 1;
            ambiente[i][j].x = 1.0 + (double)rand() / RAND_MAX * 9.0;
            ambiente[i][j].y = 1.0 + (double)rand() / RAND_MAX * 9.0;
            itens--;
        }
    }

    int ocupado[M][M];
    for (i = 0; i < M; i++) {
        for (j = 0; j < M; j++) {
            ocupado[i][j] = 0;
        }
    }

    for (int f = 0; f < NFORMIGAS; f++) {
        formigas[f].carregando = 0;
        do {
            i = rand() % M;
            j = rand() % M;
        } while (ocupado[i][j]);

        formigas[f].linha = i;
        formigas[f].col   = j;
        ocupado[i][j] = 1;
    }
}

void imprimir()
{
    char matriz[M][M];

    int i, j;

    for(i = 0; i < M; i++) {
        for (j = 0; j < M; j++) {
            matriz[i][j] = (ambiente[i][j].ocupado) ? 'X' : '.';
        }
    }

    for (int f = 0; f < NFORMIGAS; f++) {
        i = formigas[f].linha;
        j = formigas[f].col;
        matriz[i][j] = formigas[f].carregando ? 'C' : 'F';
    }
   
    for (i = 0; i < M; i++) {
        for (j = 0; j < M; j++) {
            printf("%c ", matriz[i][j]);
        }
        printf("\n");
    }
    printf("F = formiga livre; C = carregando; X = item; . = vazio\n\n");
    // mudar();
}

void mudar(int f) {
    int dl[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    int dir = rand() % 4;

    int novaL = formigas[f].linha + dl[dir];
    int novaC   = formigas[f].col   + dc[dir];
    
    if (novaL >= 0 && novaL < M &&
        novaC   >= 0 && novaC   < M) {
        formigas[f].linha = novaL;
        formigas[f].col   = novaC;
    }
}

int qtdItensVizinhanca(int linha, int col)
{
    int count = 0;
    for (int di = -RAIO; di <= RAIO; di++) {
        for (int dj = -RAIO; dj <= RAIO; dj++) {
            int ni = linha + di;
            int nj = col   + dj;
            if (ni >= 0 && ni < M && nj >= 0 && nj < M)
                if (ambiente[ni][nj].ocupado == 1)
                    count++;
        }
    }
    return count;
}

void tentarPegar(int f)
{
    if (formigas[f].carregando) return;
    int li = formigas[f].linha;
    int co = formigas[f].col;
    if (ambiente[li][co].ocupado == 0) return;

    int celulas = (2*RAIO+1)*(2*RAIO+1);
    double frac = (double)qtdItensVizinhanca(li, co) / celulas;

    double p = 1.0 - frac;

    double sorteio = (double)rand() / RAND_MAX;
    if (sorteio < p) {
        formigas[f].carregando = 1;
        ambiente[li][co].ocupado = 0;
    }
}

void tentarLargar(int f) {
    if (!formigas[f].carregando) return;
    int li = formigas[f].linha;
    int co = formigas[f].col;
    if (ambiente[li][co].ocupado == 1) return;

    int celulas = (2*RAIO+1)*(2*RAIO+1);
    double frac = (double)qtdItensVizinhanca(li, co) / celulas;

    double p = frac;

    double sorteio = (double)rand() / RAND_MAX;
    if (sorteio < p) {
        formigas[f].carregando = 0;
        ambiente[li][co].ocupado = 1;
    }
}

void simular(int passos) {
    for (int t = 0; t < passos; t++) {
        for (int f = 0; f < NFORMIGAS; f++) {
            mudar(f);
            tentarPegar(f);
            tentarLargar(f);
        }

        if ((t + 1) % 10000 == 0) {
            printf("*-*-*-*- Passo %d -*-*-*-*\n", t + 1);
            imprimir();
        }
    }
}

/*
Criar ambiente no formato de matriz
Distribuir itens (dados homogêneos) uniformemente na matriz
Criar estrutura dos agentes que atuarão no ambiente (formigas vivas): i. definir raio de visão. Usar raio 01 inicialmente; ii. estado ocupado/livre; iii. estrutura para o item a ser carregado

- precisa ser uma matriz de 64x64?
- pode mais de uma formiga por celula?
- o que é "estrutura para o item a ser carregado"
*/