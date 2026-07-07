import joblib
import pandas as pd

modelo = joblib.load("modelo_estres.pkl")

nuevo = pd.DataFrame({
    "Humidity": [25.3],
    "Temperature": [92.1],
    "Step count": [140]
})

prediccion = modelo.predict(nuevo)

print("Nivel de estrés:", prediccion[0])