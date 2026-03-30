import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib 
import os
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_CONNECTION_STRING")

# 1. Cargar datos de SQL
engine = create_engine(DB_URI)
df = pd.read_sql('SELECT * FROM v_prestamos_limpios', engine)

# 2. Definir variables (X son las causas, y es el efecto)
# Usamos las columnas numéricas que ya tenemos
columnas_x = ['edad', 'ingresos_anuales_cop', 'monto_prestamo_cop', 'tasa_interes', 'años_experiencia']
X = df[columnas_x]
y = df['estado_pago'].apply(lambda x: 1 if x == 'Moroso' else 0)

# 3. Dividir datos (80% entrenamiento, 20% prueba)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Entrenar el modelo
print("🧠 Entrenando el cerebro del modelo...")
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 5. Evaluar precisión y métricas avanzadas
predicciones = modelo.predict(X_test)
precision = accuracy_score(y_test, predicciones)

print("\n--- 📊 MÉTRICAS DEL MODELO ---")
print(f"✅ Exactitud Global (Accuracy): {precision:.2%}")

print("\n🔍 Reporte de Clasificación:")
print(classification_report(y_test, predicciones, target_names=['Al Día (0)', 'Moroso (1)']))

print("🧩 Matriz de Confusión:")
print(confusion_matrix(y_test, predicciones))
print("-------------------------------\n")

# 6. ¡GUARDAR EL MODELO EN EL DISCO DURO!
nombre_archivo = 'modelo_riesgo_final.pkl'
joblib.dump(modelo, nombre_archivo)

print(f"💾 ¡ÉXITO! El modelo se ha guardado como '{nombre_archivo}'")
print("Ahora puedes usar este archivo en cualquier otro script sin tener que volver a entrenar.")