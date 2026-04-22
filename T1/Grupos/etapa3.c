#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define M 64
#define NFORMIGAS 15
#define RAIO 1
#define NITENS 400

#define ALPHA 0.35
#define K1 0.5
#define K2 0.025

typedef struct {
    int ocupado;
    double x;
    double y;
    int grupo;
} Item;

Item ambiente[M][M];

typedef struct {
    int linha;
    int col;
    int carregando; // 0 ou 1
    Item item;
} Formiga;

Formiga formigas[NFORMIGAS];

typedef struct {
    FILE* fp;
    int   frameAtual;
} HTMLPlayer;

// IA
void htmlPlayerInicio(HTMLPlayer* p, const char* nomeArquivo);
void htmlPlayerGravarFrame(HTMLPlayer* p, int passo);
void htmlPlayerFinalizar(HTMLPlayer* p);
void imprimirHTML(const char* saida);

void inicializar(const char* arquivo);
//void inicializar();
void imprimir();
void mudar(int f);
int qtdItensVizinhanca(int linha, int col);
double dissimilaridade(Item item, int linha, int col);
void tentarPegar(int f);
void tentarLargar(int f);
void simular(int passos, HTMLPlayer* player);

int main(void)
{
    inicializar("grupo4.txt");
    //inicializar();

    printf("*-*-*-*- Passo 1 -*-*-*-*\n");
    imprimir();

    HTMLPlayer player;
    htmlPlayerInicio(&player, "simulacao.html");
    htmlPlayerGravarFrame(&player, 0);

    simular(20000000, &player);

    printf("\n*-*-*-*- Passo final -*-*-*-*\n");
    imprimir();

    htmlPlayerFinalizar(&player);

    return 0;
}

// inicializar com arquivo
void inicializar(const char* arquivo) {
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            ambiente[i][j].ocupado = 0;
            ambiente[i][j].x = 0.0;
            ambiente[i][j].y = 0.0;
            ambiente[i][j].grupo = 0;
        }
    }

    FILE* fp = fopen(arquivo, "r");
    if (!fp) { 
        perror("Erro ao abrir arquivo"); 
        exit(1); 
    }

    char linha[256];
    int nitens = 0;
    while (fgets(linha, sizeof(linha), fp) && nitens < NITENS) {
        if (linha[0] == '#' || linha[0] == '\n') continue;

        for (int k = 0; linha[k]; k++) {
            if (linha[k] == ',') {
                linha[k] = '.';
            }
        }

        double x, y;
        int grupo;
        if (sscanf(linha, "%lf %lf %d", &x, &y, &grupo) != 3) continue;

        int i, j;
        do {
            i = rand() % M;
            j = rand() % M;
        } while (ambiente[i][j].ocupado);

        ambiente[i][j].ocupado = 1;
        ambiente[i][j].x = x;
        ambiente[i][j].y = y;
        ambiente[i][j].grupo = grupo;
        nitens++;
    }
    fclose(fp);

    int ocupado[M][M] = {0};
    for (int f = 0; f < NFORMIGAS; f++) {
        formigas[f].carregando = 0;
        formigas[f].item.ocupado = 0;
        int i, j;
        do { 
            i = rand() % M; 
            j = rand() % M; 
        } while (ocupado[i][j]);

        formigas[f].linha = i;
        formigas[f].col = j;
        ocupado[i][j] = 1;
    }
}

// inicializar sem arquivo
/*void inicializar()
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
        formigas[f].item.ocupado = 0;
        formigas[f].item.x = 0.0;
        formigas[f].item.y = 0.0;
        do {
            i = rand() % M;
            j = rand() % M;
        } while (ocupado[i][j]);

        formigas[f].linha = i;
        formigas[f].col   = j;
        ocupado[i][j] = 1;
    }
}*/

void imprimir()
{
    char matriz[M][M];
    char simbolos[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9', 'U', 'V', 'W', 'X', 'Y', 'Z'};

    int i, j;

    for(i = 0; i < M; i++) {
        for (j = 0; j < M; j++) {
            matriz[i][j] = (ambiente[i][j].ocupado) ? simbolos[ambiente[i][j].grupo - 1] : '.';
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
    int novaC = formigas[f].col + dc[dir];

    if (novaL >= 0 && novaL < M && novaC >= 0 && novaC < M) {
        int ocupada = 0;
        for (int k = 0; k < NFORMIGAS; k++) {
            if (k != f && formigas[k].linha == novaL && formigas[k].col == novaC) {
                ocupada = 1;
                break;
            }
        }
        if (!ocupada) {
            formigas[f].linha = novaL;
            formigas[f].col = novaC;
        }
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

double dissimilaridade(Item item, int linha, int col) {
    double soma = 0.0;

    for (int di = -RAIO; di <= RAIO; di++) {
        for (int dj = -RAIO; dj <= RAIO; dj++) {
            int ni = linha + di;
            int nj = col + dj;
            if (ni >= 0 && ni < M && nj >= 0 && nj < M) {
                if (ambiente[ni][nj].ocupado == 1) {
                    double dx = item.x - ambiente[ni][nj].x;
                    double dy = item.y - ambiente[ni][nj].y;
                    soma += 1 - (sqrt(dx*dx + dy*dy) / ALPHA);
                }
            }
        }
    }

    int vizinhos = qtdItensVizinhanca(linha, col);
    if (vizinhos == 0) return 0;
    double f = (1.0 / ((double)vizinhos * vizinhos)) * soma;

    if(f > 0) {
        return f;
    }
    return 0;
}

void tentarPegar(int f)
{
    if (formigas[f].carregando) return;
    int li = formigas[f].linha;
    int co = formigas[f].col;
    if (ambiente[li][co].ocupado == 0) return;

    double d = dissimilaridade(ambiente[li][co], li, co);

    double p = (K1 / (K1 + d)) * (K1 / (K1 + d));

    double sorteio = (double)rand() / RAND_MAX;
    if (sorteio < p) {
        formigas[f].carregando = 1;
        formigas[f].item = ambiente[li][co];
        ambiente[li][co].ocupado = 0;
        ambiente[li][co].x = 0.0;
        ambiente[li][co].y = 0.0;
    }
}

void tentarLargar(int f) {
    if (!formigas[f].carregando) return;
    int li = formigas[f].linha;
    int co = formigas[f].col;
    if (ambiente[li][co].ocupado == 1) return;

    double d = dissimilaridade(formigas[f].item, li, co);

    double p = (d / (K2 + d)) * (d / (K2 + d));

    double sorteio = (double)rand() / RAND_MAX;
    if (sorteio < p) {
        formigas[f].carregando = 0;
        ambiente[li][co] = formigas[f].item;
        ambiente[li][co].ocupado = 1;

        formigas[f].item.ocupado = 0;
        formigas[f].item.x = 0.0;
        formigas[f].item.y = 0.0;
    }
}

void simular(int passos, HTMLPlayer* player) {
    for (int t = 0; t < passos; t++) {
        for (int f = 0; f < NFORMIGAS; f++) {
            mudar(f);
            tentarPegar(f);
            tentarLargar(f);
        }
        
        /*printf("*-*-*-*- Passo %d -*-*-*-*\n", t + 1);
        imprimir();*/
        
        if ((t + 1) % 10000 == 0) {
            //printf("*-*-*-*- Passo %d -*-*-*-*\n", t + 1);
            //imprimir();

            htmlPlayerGravarFrame(player, t + 1); // grava frame            
        }
    }
}

// Adicione esta função ao seu código C existente
// Chame imprimirHTML("resultado_final.html") no lugar ou junto com imprimir()

void imprimirHTML(const char* saida) {
    FILE* fp = fopen(saida, "w");
    if (!fp) { perror("Erro ao criar HTML"); return; }

    // Cores por grupo (até 6 grupos)
    const char* cores[] = {
        "#FF0000", // red
        "#00FF00", // green
        "#0000FF", // blue
        "#FFFF00", // yellow
        "#FF00FF", // magenta
        "#00FFFF", // cyan
        "#FFA500", // orange
        "#800080", // purple
        "#FFC0CB", // pink
        "#FF4500", // orange red
        "#32CD32", // lime green
        "#000080", // navy
        "#FFD700", // gold
        "#DC143C", // crimson
        "#00CED1", // dark turquoise
    };
    const char* coresClaras[] = {
        "#B5D4F4",
        "#F5C4B3",
        "#9FE1CB",
        "#FAC775",
        "#AFA9EC",
        "#F4C0D1"
    };

    fprintf(fp,
        "<!DOCTYPE html><html lang='pt-br'><head><meta charset='UTF-8'>"
        "<title>Ant Clustering</title>"
        "<style>"
        "  body { background: #0f0f0f; font-family: monospace; display: flex;"
        "         flex-direction: column; align-items: center; padding: 24px; margin: 0; }"
        "  h1 { color: #e0e0e0; font-size: 18px; font-weight: 400; letter-spacing: 4px;"
        "       text-transform: uppercase; margin-bottom: 8px; }"
        "  #legenda { display: flex; gap: 16px; margin: 12px 0 16px; flex-wrap: wrap; justify-content: center; }"
        "  .leg { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #aaa; }"
        "  .leg-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }"
        "  #grade { display: grid; gap: 1px; background: #1a1a1a;"
        "           border: 1px solid #2a2a2a; border-radius: 8px; overflow: hidden; }"
        "  .cel { width: 9px; height: 9px; }"
        "  .cel.vazio { background: #1a1a1a; }"
        "  .cel.formiga { background: #555; border-radius: 50%%; }"
        "  .cel.carregando { background: #fff; border-radius: 50%%; }"
        "  .cel.item { border-radius: 50%%; }"
        "  #stats { margin-top: 16px; color: #666; font-size: 12px; letter-spacing: 1px; }"
        "</style></head><body>"
        "<h1>Ant Clustering</h1>"
        "<div id='legenda'>"
    );

    // Legenda dos grupos
    for (int g = 0; g < 15; g++) {
        fprintf(fp,
            "<div class='leg'>"
            "<span class='leg-dot' style='background:%s'></span>"
            "<span>Grupo %d</span></div>",
            cores[g], g + 1
        );
    }
    fprintf(fp,
        "<div class='leg'><span class='leg-dot' style='background:#555'></span><span>Formiga</span></div>"
        "<div class='leg'><span class='leg-dot' style='background:#fff'></span><span>Carregando</span></div>"
        "</div>"
    );

    // Grade
    fprintf(fp, "<div id='grade' style='grid-template-columns: repeat(%d, 9px);'>", M);

    // Monta mapa de formigas para lookup rápido
    int mapa_formigas[M][M];
    for (int i = 0; i < M; i++)
        for (int j = 0; j < M; j++)
            mapa_formigas[i][j] = -1; // -1 = sem formiga

    for (int f = 0; f < NFORMIGAS; f++)
        mapa_formigas[formigas[f].linha][formigas[f].col] = formigas[f].carregando ? 2 : 1;

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            int fm = mapa_formigas[i][j];

            if (fm == 2) {
                // Formiga carregando item (branco)
                fprintf(fp, "<div class='cel carregando' title='Carregando'></div>");
            } else if (fm == 1) {
                // Formiga livre
                fprintf(fp, "<div class='cel formiga' title='Formiga'></div>");
            } else if (ambiente[i][j].ocupado) {
                int g = ambiente[i][j].grupo - 1;
                if (g < 0) g = 0;
                if (g > 14) g = 14;
                fprintf(fp,
                    "<div class='cel item' style='background:%s' title='Grupo %d (%.2f, %.2f)'></div>",
                    cores[g], g + 1, ambiente[i][j].x, ambiente[i][j].y
                );
            } else {
                fprintf(fp, "<div class='cel vazio'></div>");
            }
        }
    }

    // Contagem por grupo
    int contagem[16] = {0};
    for (int i = 0; i < M; i++)
        for (int j = 0; j < M; j++)
            if (ambiente[i][j].ocupado && ambiente[i][j].grupo >= 1 && ambiente[i][j].grupo <= 15)
                contagem[ambiente[i][j].grupo]++;

    fprintf(fp, "</div><div id='stats'>Itens no mapa: ");
    for (int g = 1; g <= 15; g++)
        if (contagem[g] > 0)
            fprintf(fp, "G%d=%d  ", g, contagem[g]);
    fprintf(fp, "</div></body></html>\n");

    fclose(fp);
    printf("[HTML salvo em: %s]\n", saida);
}

// =============================================================
// Substitua as funções de HTML antigas por estas duas abaixo
// =============================================================
//
// USO no main / simular():
//
//   HTMLPlayer player;
//   htmlPlayerInicio(&player, "simulacao.html");
//
//   // dentro do loop de simulação, onde quiser gravar um frame:
//   htmlPlayerGravarFrame(&player);
//
//   // ao final:
//   htmlPlayerFinalizar(&player);
//
// =============================================================

void htmlPlayerInicio(HTMLPlayer* p, const char* nomeArquivo) {
    p->fp = fopen(nomeArquivo, "w");
    p->frameAtual = 0;

    if (!p->fp) { perror("Erro ao criar HTML"); return; }

    fprintf(p->fp,
        "<!DOCTYPE html><html lang='pt-br'><head><meta charset='UTF-8'>"
        "<title>Ant Clustering — Player</title>"
        "<style>"
        "  * { box-sizing: border-box; margin: 0; padding: 0; }"
        "  body { background:#0f0f0f; font-family:monospace;"
        "         display:flex; flex-direction:column; align-items:center;"
        "         padding:24px; gap:14px; }"
        "  h1 { color:#e0e0e0; font-size:16px; font-weight:400;"
        "       letter-spacing:4px; text-transform:uppercase; }"
        "  #grade { display:grid; gap:1px; background:#111;"
        "           border:1px solid #2a2a2a; border-radius:8px; overflow:hidden;"
        "           grid-template-columns: repeat(%d, 9px); }"
        "  .cel { width:9px; height:9px; }"
        "  #controles { display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:center; }"
        "  button { background:transparent; color:#ccc; border:1px solid #444;"
        "           padding:6px 16px; cursor:pointer; font-family:monospace;"
        "           font-size:13px; border-radius:4px; }"
        "  button:hover { background:#222; color:#fff; }"
        "  #slider { width:340px; accent-color:#378ADD; }"
        "  #info { color:#666; font-size:12px; letter-spacing:1px; }"
        "  #legenda { display:flex; gap:14px; flex-wrap:wrap; justify-content:center; }"
        "  .leg { display:flex; align-items:center; gap:6px; font-size:12px; color:#888; }"
        "  .leg-dot { width:10px; height:10px; border-radius:50%; }"
        "</style></head><body>"
        "<h1>Ant Clustering</h1>"
        "<div id='legenda'>"
        "  <div class='leg'><span class='leg-dot' style='background:#FF0000'></span>Grupo 1</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#00FF00'></span>Grupo 2</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#0000FF'></span>Grupo 3</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FFFF00'></span>Grupo 4</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FF00FF'></span>Grupo 5</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#00FFFF'></span>Grupo 6</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FFA500'></span>Grupo 7</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#800080'></span>Grupo 8</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FFC0CB'></span>Grupo 9</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FF4500'></span>Grupo 10</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#32CD32'></span>Grupo 11</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#000080'></span>Grupo 12</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#FFD700'></span>Grupo 13</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#DC143C'></span>Grupo 14</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#00CED1'></span>Grupo 15</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#555'></span>Formiga</div>"
        "  <div class='leg'><span class='leg-dot' style='background:#fff'></span>Carregando</div>"
        "</div>"
        "<div id='controles'>"
        "  <button onclick='irParaPrimeiro()'>|◀</button>"
        "  <button onclick='voltarFrame()'>◀</button>"
        "  <button id='btnPlay' onclick='togglePlay()'>▶ Play</button>"
        "  <button onclick='avancarFrame()'>▶</button>"
        "  <button onclick='irParaUltimo()'>▶|</button>"
        "  <input type='range' id='slider' value='0' min='0' step='1' oninput='irParaFrame(+this.value)'>"
        "</div>"
        "<div id='info'>Carregando...</div>"
        "<div id='grade'></div>"
        "<script>\n"
        "const CORES=['#0f0f0f','#FF0000','#00FF00','#0000FF','#FFFF00','#FF00FF','#00FFFF','#FFA500','#800080','#FFC0CB','#FF4500','#32CD32','#000080','#FFD700','#DC143C','#00CED1'];\n"
        "const frames=[];\n"
        "const labels=[];\n",
        M
    );
}

void htmlPlayerGravarFrame(HTMLPlayer* p, int passo) {
    if (!p->fp) return;

    // Monta mapa de formigas
    int mapa[M][M];
    for (int i = 0; i < M; i++)
        for (int j = 0; j < M; j++)
            mapa[i][j] = 0;

    for (int f = 0; f < NFORMIGAS; f++) {
        int li = formigas[f].linha;
        int co = formigas[f].col;
        mapa[li][co] = formigas[f].carregando ? -2 : -1; // -1=formiga, -2=carregando
    }

    // Serializa frame como array compacto: 0=vazio, -1=formiga, -2=carregando, 1-6=grupo
    fprintf(p->fp, "frames.push([");
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            int val = 0;
            if (mapa[i][j] == -2)       val = -2;
            else if (mapa[i][j] == -1)  val = -1;
            else if (ambiente[i][j].ocupado) val = ambiente[i][j].grupo;
            fprintf(p->fp, "%d", val);
            if (!(i == M-1 && j == M-1)) fprintf(p->fp, ",");
        }
    }
    fprintf(p->fp, "]);\n");
    fprintf(p->fp, "labels.push('Passo %d');\n", passo);

    p->frameAtual++;
}

void htmlPlayerFinalizar(HTMLPlayer* p) {
    if (!p->fp) return;

    fprintf(p->fp,
        "const M=%d;\n"
        "const total=frames.length;\n"
        "let frameIdx=0, playing=false, intervalo=null;\n"
        "const grade=document.getElementById('grade');\n"
        "const slider=document.getElementById('slider');\n"
        "const info=document.getElementById('info');\n"
        "slider.max=total-1;\n"
        "\n"
        "// Cria células uma vez\n"
        "const cels=[];\n"
        "for(let i=0;i<M*M;i++){\n"
        "  const d=document.createElement('div');\n"
        "  d.className='cel';\n"
        "  grade.appendChild(d);\n"
        "  cels.push(d);\n"
        "}\n"
        "\n"
        "function renderFrame(idx){\n"
        "  const f=frames[idx];\n"
        "  for(let i=0;i<f.length;i++){\n"
        "    const v=f[i];\n"
        "    const c=cels[i];\n"
        "    if(v===-2){ c.style.background='#ffffff'; c.style.borderRadius='50%%'; }\n"
        "    else if(v===-1){ c.style.background='#555555'; c.style.borderRadius='50%%'; }\n"
        "    else if(v>0){ c.style.background=CORES[v]; c.style.borderRadius='50%%'; }\n"
        "    else { c.style.background='#111111'; c.style.borderRadius='0'; }\n"
        "  }\n"
        "  info.textContent=labels[idx]+' — frame '+(idx+1)+'/'+total;\n"
        "  slider.value=idx;\n"
        "}\n"
        "\n"
        "function avancarFrame(){ if(frameIdx<total-1){frameIdx++;renderFrame(frameIdx);} }\n"
        "function voltarFrame(){ if(frameIdx>0){frameIdx--;renderFrame(frameIdx);} }\n"
        "function irParaFrame(n){ frameIdx=n; renderFrame(frameIdx); }\n"
        "function irParaPrimeiro(){ frameIdx=0; renderFrame(0); }\n"
        "function irParaUltimo(){ frameIdx=total-1; renderFrame(frameIdx); }\n"
        "function togglePlay(){\n"
        "  playing=!playing;\n"
        "  document.getElementById('btnPlay').textContent=playing?'⏸ Pause':'▶ Play';\n"
        "  if(playing){\n"
        "    intervalo=setInterval(()=>{\n"
        "      if(frameIdx>=total-1){ clearInterval(intervalo); playing=false;\n"
        "        document.getElementById('btnPlay').textContent='▶ Play'; return; }\n"
        "      frameIdx++; renderFrame(frameIdx);\n"
        "    },300);\n"
        "  } else { clearInterval(intervalo); }\n"
        "}\n"
        "renderFrame(0);\n"
        "</script></body></html>\n",
        M
    );

    fclose(p->fp);
    //printf("[Player HTML salvo!]\n");
}

/*
Criar ambiente no formato de matriz
Distribuir itens (dados homogêneos) uniformemente na matriz
Criar estrutura dos agentes que atuarão no ambiente (formigas vivas): i. definir raio de visão. Usar raio 01 inicialmente; ii. estado ocupado/livre; iii. estrutura para o item a ser carregado

- precisa ser uma matriz de 64x64?
- pode mais de uma formiga por celula?
- o que é "estrutura para o item a ser carregado"
*/