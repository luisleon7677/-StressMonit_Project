import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Leer dataset
df = pd.read_csv("data/Stress-Lysis.csv")

# Variables independientes
X = df[["Humidity", "Temperature", "Step count"]]

# Variable objetivo
y = df["Stress Level"]

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Crear modelo
modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Entrenar
modelo.fit(X_train, y_train)

# Evaluar
predicciones = modelo.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predicciones))
print(classification_report(y_test, predicciones))

# Guardar modelo
joblib.dump(modelo, "modelo_estres.pkl")

print("Modelo entrenado correctamente.")