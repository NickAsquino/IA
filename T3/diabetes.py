import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------
# ETAPA 1: CARREGAMENTO DOS DADOS
# ---------------------------------------------------------
# Agora apontando para o arquivo verdadeiro com os dados!
arquivo = 'diabetesdataset.csv'

print("\n--- 1. Carregando os Dados ---")
df = pd.read_csv(arquivo)
print(df.head()) # Vai imprimir os 5 primeiros pacientes

# ---------------------------------------------------------
# INVESTIGAÇÃO: Zeros fisiologicamente impossíveis
# ---------------------------------------------------------
colunas_suspeitas = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

print("\n--- Proporção de zeros em colunas que não podem ser zero ---")
for col in colunas_suspeitas:
    qtd_zeros = (df[col] == 0).sum()
    pct_zeros = 100 * qtd_zeros / len(df)
    print(f"{col}: {qtd_zeros} zeros ({pct_zeros:.1f}% dos dados)")

# ---------------------------------------------------------
# TRATAMENTO: Imputação pela mediana
# ---------------------------------------------------------
for col in colunas_suspeitas:
    df[col] = df[col].replace(0, np.nan)
    mediana = df[col].median()
    df[col] = df[col].fillna(mediana)

print("\n--- Após tratamento: zeros restantes ---")
for col in colunas_suspeitas:
    print(f"{col}: {(df[col] == 0).sum()} zeros")

X = df.drop('Outcome', axis=1)
y = df['Outcome']

# ---------------------------------------------------------
# ETAPA 2 e 3: PRÉ-PROCESSAMENTO E VISUALIZAÇÃO
# ---------------------------------------------------------
# Inicializando o StandardScaler (Obrigatório para igualar escalas diferentes)
scaler = StandardScaler()
X_escalado = scaler.fit_transform(X)
df_escalado = pd.DataFrame(X_escalado, columns=X.columns)

# Boxplot das features padronizadas, para detectar outliers
plt.figure(figsize=(12, 6))
df_escalado.boxplot(rot=45)
plt.title('Boxplot das Features (Padronizadas)')
plt.ylabel('Valor padronizado (z-score)')
plt.tight_layout()
plt.show()

# Matriz de correlação entre todas as features e o Outcome
correlacao = df.corr()
print("\nMatriz de Correlação:")
print(correlacao['Outcome'].sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(9, 8))
cax = ax.matshow(correlacao, cmap='coolwarm', vmin=-1, vmax=1)
fig.colorbar(cax)
ax.set_xticks(range(len(correlacao.columns)))
ax.set_yticks(range(len(correlacao.columns)))
ax.set_xticklabels(correlacao.columns, rotation=90)
ax.set_yticklabels(correlacao.columns)

for i in range(len(correlacao.columns)):
    for j in range(len(correlacao.columns)):
        ax.text(j, i, f"{correlacao.iloc[i, j]:.2f}", ha='center', va='center', fontsize=7)

plt.title('Correlação entre Features e Outcome', pad=30)
plt.tight_layout()
plt.show()

# Gráfico de Dispersão (Visualizando Glicose vs IMC)
plt.figure(figsize=(8, 6))
scatter = plt.scatter(df_escalado['Glucose'], df_escalado['BMI'], c=y, cmap='coolwarm', alpha=0.7)
plt.title('Distribuição: Glicose vs IMC')
plt.xlabel('Glicose (Padronizada)')
plt.ylabel('IMC (Padronizado)')
cbar = plt.colorbar(scatter)
cbar.set_label('0: Não-diabético | 1: Diabético')
plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# ETAPA 5: SEPARAÇÃO DOS DADOS (70 / 15 / 15)
# ---------------------------------------------------------
print("\n--- 5. Separação dos Dados ---")
X_treino, X_temp, y_treino, y_temp = train_test_split(
    X_escalado, y, 
    test_size=0.30,      
    random_state=42,     
    stratify=y
)

X_val, X_teste, y_val, y_teste = train_test_split(
    X_temp, y_temp, 
    test_size=0.50,      
    random_state=42, 
    stratify=y_temp
)

print(f"Total de pacientes: {len(X_escalado)}")
print(f"Treino (70%): {X_treino.shape[0]} pacientes")
print(f"Validação (15%): {X_val.shape[0]} pacientes")
print(f"Teste (15%): {X_teste.shape[0]} pacientes")

# ---------------------------------------------------------
# ETAPA 6: CONSTRUÇÃO DA REDE NEURAL (MLP)
# ---------------------------------------------------------
print("\n--- 6. Construção do Modelo ---")
model = keras.Sequential([
    layers.Input(shape=(8,)), 
    
    layers.Dense(units=32, activation='relu'),
    # NOVIDADE: Desliga 20% dos neurônios aleatoriamente para evitar a "decoreba"
    layers.Dropout(0.2), 
    
    layers.Dense(units=16, activation='relu'),
    # NOVIDADE: Desliga mais 20% aqui
    layers.Dropout(0.2),
    
    layers.Dense(units=2, activation='softmax')
])
model.summary()

# ---------------------------------------------------------
# ETAPA 7 E 8: TREINAMENTO E CONVERGÊNCIA
# ---------------------------------------------------------
print("\n--- 7 e 8. Treinamento e Validação ---")
model.compile(
    optimizer='adam', 
    loss='sparse_categorical_crossentropy', 
    metrics=['accuracy'] 
)

history = model.fit(
    X_treino, 
    y_treino, 
    # Reduzimos as épocas, pois vimos no gráfico que depois de 40 ela só decora
    epochs=40,          
    batch_size=16,       
    validation_data=(X_val, y_val), 
    verbose=1            
)

# Plotando a Convergência
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history.history['accuracy'], label='Treino', color='blue')
ax1.plot(history.history['val_accuracy'], label='Validação', color='orange')
ax1.set_title('Convergência da Acurácia')
ax1.set_xlabel('Épocas')
ax1.set_ylabel('Acurácia')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.6)

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

cm = confusion_matrix(y_teste, y_pred)

fig, ax = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap='Blues', values_format='d', ax=ax)
plt.title('Matriz de Confusão - Conjunto de Teste')
plt.tight_layout()
plt.show()

print(classification_report(y_teste, y_pred, target_names=['Não-diabético', 'Diabético']))

test_loss, test_accuracy = model.evaluate(X_teste, y_teste, verbose=0)
print(f"\nAcurácia final no conjunto de teste: {test_accuracy:.4f}")
print(f"Loss final no conjunto de teste: {test_loss:.4f}")