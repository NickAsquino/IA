import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler # Importando o StandardScaler
from sklearn.model_selection import train_test_split

arquivo = 'base15.txt'#'base.txt'

#base.txt
# df = pd.read_csv(
#     arquivo, 
#     sep=r'\s+',            # aceita qualquer quantidade de espaços ou TABs como separador
#     decimal=',',         # a vírgula é o separador decimal
#     header=None,         # o arquivo não tem cabeçalho
#     comment='#',          # ignorar qualquer linha que comece com '#', ou seja comentários
#     skip_blank_lines=True  # Pula qualquer linha em branco 
# )

#base15.txt
df = pd.read_csv(
    arquivo, 
    sep=r'\s+',            # aceita qualquer quantidade de espaços ou TABs como separador
    decimal='.',           # ALTERADO: agora o separador decimal é o ponto!
    header=None,           # o arquivo não tem cabeçalho
    comment='#',           # ignorar comentários
    skip_blank_lines=True  # Pula linhas em branco 
)

df.columns = ['Feature_1', 'Feature_2', 'Label']
print(df.head(10)) # print das primeiras linhas

df[['Feature_1', 'Feature_2']].hist(
    bins=20,              # quantidade de "barras" 
    figsize=(10, 5),      # largura, altura
    edgecolor='black',    # Cor da borda das barras para facilitar a leitura
    color='yellow'       # Cor das barras
)

plt.suptitle('Histograma das Features')
plt.show()

# Boxplot por classe, para detectar outliers dentro de cada cluster
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

df.boxplot(column='Feature_1', by='Label', ax=axes[0])
axes[0].set_title('Feature_1 por Classe')
axes[0].set_xlabel('Classe (Label)')
axes[0].set_ylabel('Feature_1')

df.boxplot(column='Feature_2', by='Label', ax=axes[1])
axes[1].set_title('Feature_2 por Classe')
axes[1].set_xlabel('Classe (Label)')
axes[1].set_ylabel('Feature_2')

plt.suptitle('Boxplot das Features por Classe')
plt.tight_layout()
plt.show()

# Matriz de correlação entre as features
correlacao = df[['Feature_1', 'Feature_2']].corr()
print("\nMatriz de Correlação:")
print(correlacao)

fig, ax = plt.subplots(figsize=(5, 4))
cax = ax.matshow(correlacao, cmap='coolwarm', vmin=-1, vmax=1)
fig.colorbar(cax)
ax.set_xticks(range(len(correlacao.columns)))
ax.set_yticks(range(len(correlacao.columns)))
ax.set_xticklabels(correlacao.columns)
ax.set_yticklabels(correlacao.columns)

# Escreve o valor numérico dentro de cada célula
for i in range(len(correlacao.columns)):
    for j in range(len(correlacao.columns)):
        ax.text(j, i, f"{correlacao.iloc[i, j]:.2f}", ha='center', va='center')

plt.title('Correlação entre Features', pad=20)
plt.tight_layout()
plt.show()

X = df[['Feature_1', 'Feature_2']]
y = df['Label']

# 2. Inicializando o StandardScaler
scaler = StandardScaler()
X_escalado = scaler.fit_transform(X)
df_escalado = pd.DataFrame(X_escalado, columns=['Feature_1', 'Feature_2'])


# Define o tamanho da imagem (largura, altura)
plt.figure(figsize=(8, 6))

scatter = plt.scatter(df_escalado['Feature_1'], df_escalado['Feature_2'], c=y, cmap='viridis', alpha=0.8)
# Adiciona título e rótulos aos eixos
plt.title('Distribuição das Classes')
plt.xlabel('Feature 1 (Eixo X)')
plt.ylabel('Feature 2 (Eixo Y)')

# Adiciona a barra lateral para mostrar qual cor representa qual Label (1, 2, 3 ou 4)
cbar = plt.colorbar(scatter)
cbar.set_label('Classes (Labels)')

# Ajusta as margens e mostra o gráfico
plt.tight_layout()
plt.show()

print("\nSeparação dos Dados")

# 1ª Divisão: Separar 70% para Treino e 30% para um conjunto Temporário
X_treino, X_temp, y_treino, y_temp = train_test_split(
    X_escalado, y, 
    test_size=0.30,      # 30% vai para o temp, 70% fica no treino
    random_state=42,     # Trava a semente aleatória para o resultado ser sempre igual
    stratify=y
)

# 2ª Divisão: Cortar os 30% (temp) exatamente no meio para virar Validação e Teste
X_val, X_teste, y_val, y_teste = train_test_split(
    X_temp, y_temp, 
    test_size=0.50,      # 50% dos 30% = 15% para cada lado
    random_state=42, 
    stratify=y_temp
)

print(f"Total de itens: {len(X_escalado)}")
print(f"Treino (70%): {X_treino.shape[0]} itens")
print(f"Validação (15%): {X_val.shape[0]} itens")
print(f"Teste (15%): {X_teste.shape[0]} itens")

print("\nEtapa 6")

# Importante: Como o Keras prefere que as classes comecem do zero (0, 1, 2, 3) 
# em vez de (1, 2, 3, 4), vamos fazer um pequeno ajuste rápido nos seus labels 
# para evitar um erro chato na próxima etapa:
y_treino_ajustado = y_treino - 1
y_val_ajustado = y_val - 1
y_teste_ajustado = y_teste - 1

# Inicializando o modelo Sequencial
model = keras.Sequential([
    # forma recomendada pelo Keras para a camada de entrada
    layers.Input(shape=(2,)), 
    
    # Camadas Ocultas para base.txt
    #layers.Dense(units=16, activation='relu'),
    #layers.Dense(units=8, activation='relu'),

    # base15.txt
    layers.Dense(units=64, activation='relu'),
    layers.Dense(units=32, activation='relu'),
    
    # Camada de Saída
    #layers.Dense(units=4, activation='softmax')
    layers.Dense(units=15, activation='softmax')
])
model.summary()

print("\nEtapa 7 e 8")

# COMPILAÇÃO 
model.compile(
    optimizer='adam', # Usando o Adam (ele já gerencia o Learning Rate muito bem)
    loss='sparse_categorical_crossentropy', 
    metrics=['accuracy'] # Queremos medir a Acurácia (taxa de acertos)
)

# TREINAMENTO (Forward/Backpropagation na prática)
history = model.fit(
    X_treino, 
    y_treino_ajustado, 
    epochs=100,          # A IA vai ler os dados de treino 100 vezes
    batch_size=16,       # Ela vai estudar em lotes de 16 em 16 itens
    validation_data=(X_val, y_val_ajustado), # A cada época, ela faz o simulado
    verbose=1            # Mostra uma barra de progresso no terminal
)

# VALIDAÇÃO
# Vamos criar uma janela com 2 gráficos (Acurácia e Erro/Loss)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Acurácia (Taxa de Acerto - Quanto maior, melhor)
ax1.plot(history.history['accuracy'], label='Treino', color='blue')
ax1.plot(history.history['val_accuracy'], label='Validação', color='orange')
ax1.set_title('Convergência da Acurácia')
ax1.set_xlabel('Épocas')
ax1.set_ylabel('Acurácia')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.6)

# Gráfico 2: Loss (Erro - Quanto menor, melhor)
ax2.plot(history.history['loss'], label='Treino', color='blue')
ax2.plot(history.history['val_loss'], label='Validação', color='orange')
ax2.set_title('Queda do Erro (Loss)')
ax2.set_xlabel('Épocas')
ax2.set_ylabel('Erro')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

print("\nEtapa 9 - Avaliação Final no Conjunto de Teste")

y_pred_prob = model.predict(X_teste)
y_pred = y_pred_prob.argmax(axis=1)

cm = confusion_matrix(y_teste_ajustado, y_pred)

fig, ax = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap='Blues', values_format='d', ax=ax)
plt.title('Matriz de Confusão - Conjunto de Teste')
plt.tight_layout()
plt.show()

print(classification_report(y_teste_ajustado, y_pred))

test_loss, test_accuracy = model.evaluate(X_teste, y_teste_ajustado, verbose=0)
print(f"\nAcurácia final no conjunto de teste: {test_accuracy:.4f}")
print(f"Loss final no conjunto de teste: {test_loss:.4f}")