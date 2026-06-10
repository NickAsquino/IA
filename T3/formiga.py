import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import os
os.makedirs('graficos', exist_ok=True)

arquivo = 'base600.txt'
df = pd.read_csv(
    arquivo,
    sep=r'\s+',
    # decimal=',', # base 400
    decimal='.', # base 600
    header=None,
    comment='#',
    skip_blank_lines=True
)
df.columns = ['Feature_1', 'Feature_2', 'Label']

# Histogramas
df[['Feature_1', 'Feature_2']].hist(bins=20, figsize=(10, 5), edgecolor='black', color='yellow')
plt.suptitle('Histograma das Features')
plt.tight_layout()
plt.savefig('graficos/histogramas.png', dpi=150)
plt.show()

# Boxplot
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, col in zip(axes, ['Feature_1', 'Feature_2']):
    df.boxplot(column=col, ax=ax)
    ax.set_title(f'Boxplot — {col}')
plt.tight_layout()
plt.savefig('graficos/boxplots.png', dpi=150)
plt.show()

# Correlação
print("\nCorrelação entre features:")
print(df[['Feature_1', 'Feature_2']].corr())

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 3: dados faltantes

print("\n=== Valores faltantes por coluna ===")
print(df.isnull().sum())
print(f"Total de faltantes: {df.isnull().sum().sum()}")
df_tratado = df.copy()

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 4 e etapa 5: escalonamento

X = df[['Feature_1', 'Feature_2']]
y = df['Label']

# 1ª Divisão: Separar 70% para Treino e 30% para um conjunto Temporário
X_treino, X_temp, y_treino, y_temp = train_test_split(
    X, y, 
    test_size = 0.30,      # 30% vai para o temp, 70% fica no treino
    random_state = 42,     # Trava a semente aleatória para o resultado ser sempre igual
    stratify = y
)

# 2ª Divisão: Cortar os 30% (temp) exatamente no meio para virar Validação e Teste
X_val, X_teste, y_val, y_teste = train_test_split(
    X_temp, y_temp, 
    test_size=0.50,      # 50% dos 30% = 15% para cada lado
    random_state=42, 
    stratify=y_temp
)

# 2. Inicializando o StandardScaler
scaler = StandardScaler()
X_treino = scaler.fit_transform(X_treino)
X_val    = scaler.transform(X_val)
X_teste  = scaler.transform(X_teste)

df_escalado = pd.DataFrame(X_treino, columns=['Feature_1', 'Feature_2'])
plt.figure(figsize=(8, 6))
scatter = plt.scatter(
    scaler.inverse_transform(X_treino)[:, 0],
    scaler.inverse_transform(X_treino)[:, 1],
    c=y_treino, cmap='tab20', alpha=0.8
)
plt.colorbar(scatter, label='Classes (Labels)')
plt.title('Distribuição das Classes (Treino)')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.tight_layout()
plt.savefig('graficos/scatter_classes.png', dpi=150)
plt.show()

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 6 : MLP

# Importante: Como o Keras prefere que as classes comecem do zero (0, 1, 2, 3) 
# em vez de (1, 2, 3, 4), vamos fazer um pequeno ajuste rápido nos seus labels 
# para evitar um erro chato na próxima etapa:
y_treino_ajustado = y_treino - 1
y_val_ajustado = y_val - 1
y_teste_ajustado = y_teste - 1

# Inicializando o modelo Sequencial
model = keras.Sequential([
    layers.Input(shape=(2,)),     
    # layers.Dense(units=16, activation='relu', kernel_regularizer=regularizers.l2(0.001)), # base 400
    # layers.Dense(units=8, activation='relu', kernel_regularizer=regularizers.l2(0.001)), # base 400
    # layers.Dense(units=4, activation='softmax') # base 400
    layers.Dense(units=64, activation='relu', kernel_regularizer=regularizers.l2(0.001)), # base 600
    layers.Dense(units=32, activation='relu', kernel_regularizer=regularizers.l2(0.001)), # base 600
    layers.Dense(units=15, activation='softmax') # base 600
])
model.summary()

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 7 : Treinamento

# COMPILAÇÃO 
model.compile(
    optimizer='adam', # Usando o Adam (ele já gerencia o Learning Rate muito bem)
    loss='sparse_categorical_crossentropy', 
    metrics=['accuracy'] # Queremos medir a Acurácia (taxa de acertos)
)

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

# TREINAMENTO (Forward/Backpropagation na prática)
history = model.fit(
    X_treino, 
    y_treino_ajustado, 
    epochs=100,          # A IA vai ler os dados de treino 100 vezes
    batch_size=16,       # Ela vai estudar em lotes de 16 em 16 itens
    validation_data=(X_val, y_val_ajustado), # A cada época, ela faz o simulado
    callbacks=[early_stop],
    verbose=1            # Mostra uma barra de progresso no terminal
)

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 8 : Validacao

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
plt.savefig('graficos/curvas_aprendizado.png', dpi=150)
plt.show()

# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
# Etapa 9 : teste final

y_pred = np.argmax(model.predict(X_teste), axis=1)  # pega a classe com maior probabilidade

# ACURACIA
loss_teste, acc_teste = model.evaluate(X_teste, y_teste_ajustado, verbose=0)
print(f"\nAcurácia no Teste: {acc_teste * 100:.2f}%")
print(f"Loss no Teste:     {loss_teste:.4f}")

# RELATORIO
print("\nRelatorio de Classificacao")
print(classification_report(
    y_teste_ajustado,
    y_pred,
    # target_names=['Classe 1', 'Classe 2', 'Classe 3', 'Classe 4'] # base 400
    target_names=[f'Classe {i}' for i in range(1, 16)] # base 600
))

# MATRIZ DE CONFUSAO
cm = confusion_matrix(y_teste_ajustado, y_pred)
fig, ax = plt.subplots(figsize=(14, 12))
ConfusionMatrixDisplay(
    confusion_matrix=cm,
    # display_labels=['Classe 1', 'Classe 2', 'Classe 3', 'Classe 4'] # base 400
    display_labels=[f'Classe {i}' for i in range(1, 16)] # base 600
).plot(ax=ax, cmap='Blues', colorbar=False)
ax.set_title('Matriz de Confusão — Conjunto de Teste')
plt.tight_layout()
plt.savefig('graficos/matriz_confusao.png', dpi=150)
plt.show()