import pandas as pd
import joblib
from sqlalchemy import create_engine
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. Cargar el Cerebro (ML) y la IA (Gemini)
modelo_ml = joblib.load('modelo_riesgo_final.pkl')
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. Conectar a SQL y traer un cliente nuevo al azar
engine = create_engine(DB_URI)
df_nuevo = pd.read_sql('SELECT * FROM v_prestamos_limpios ORDER BY RANDOM() LIMIT 1', engine)
cliente = df_nuevo.iloc[0]

# 3. EL MODELO MATEMÁTICO PREDICE EL FUTURO
datos_para_predecir = df_nuevo[['edad', 'ingresos_anuales_cop', 'monto_prestamo_cop', 'tasa_interes', 'años_experiencia']]
probabilidad = modelo_ml.predict_proba(datos_para_predecir)[0][1] # Probabilidad de ser moroso
resultado_ml = "ALTO RIESGO" if probabilidad > 0.5 else "BAJO RIESGO"

# 4. EL MODELO DE LENGUAJE EXPLICA EL RESULTADO
prompt = f"""
Actúa como un Auditor de Riesgos con IA. 
Mi modelo de Machine Learning dice que este cliente tiene un {probabilidad:.2%} de probabilidad de MORA.
El resultado es: {resultado_ml}.

DATOS DEL CLIENTE:
- Ingresos: ${cliente['ingresos_anuales_cop']:,} COP
- Monto: ${cliente['monto_prestamo_cop']:,} COP
- Motivo: {cliente['motivo_prestamo']}
- Depto: {cliente['departamento']}

TAREA: Justifica técnicamente por qué el modelo dio esa probabilidad y da una orden final.
"""

print(f"---  El Modelo de ML dice: {probabilidad:.2%} de Riesgo ---")
print("---  Gemini está redactando la justificación... ---\n")

try:
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    print(response.text)
except Exception as e:
    print(f"Error generando justificación: {e}")