import pandas as pd
from sqlalchemy import create_engine
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
print("--- TUS MODELOS DISPONIBLES ---")
try:
    for m in client.models.list():
        print(f"Modelo: {m.name}")
except Exception as e:
    print(f"Error al listar: {e}")

engine = create_engine(DB_URI)

query = "SELECT * FROM v_prestamos_limpios LIMIT 1"
df = pd.read_sql(query, engine)

if df.empty:
    print("No se encontraron datos en la vista.")
else:
    cliente = df.iloc[0]
    
    prompt = f"""
    Actúa como un Senior Risk Officer de un banco en Colombia. 
    Analiza el siguiente caso de crédito y redacta un reporte ejecutivo breve (máximo 2 párrafos).

    DATOS DEL CLIENTE:
    - ID Anonimizado: {cliente['id_cliente_anonimizado']}
    - Departamento: {cliente['departamento']}
    - Ingresos Anuales: ${cliente['ingresos_anuales_cop']:,} COP
    - Edad: {cliente['edad']} años
    - Motivo del Préstamo: {cliente['motivo_prestamo']}
    - Monto solicitado: ${cliente['monto_prestamo_cop']:,} COP
    - Tasa de Interés: {cliente['tasa_interes']}%
    - Estado actual: {cliente['estado_pago']}
    - Fecha Desembolso: {cliente['fecha_desembolso']}

    TAREA:
    1. Evalúa el riesgo basado en la relación Ingreso vs Monto y el departamento.
    2. Menciona una recomendación de ciberseguridad o cobranza estacional para este caso.
    """

    print("--- Generando Reporte de IA para el cliente ---")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        print("\n REPORTE GENERADO CON ÉXITO POR EL AGENTE IA:\n")
        print("====================================================")
        print(response.text)
        print("====================================================")
        
    except Exception as e:
        print(f"\n Error: {e}")
        print("\n Tip: Si sale 'Resource Exhausted', espera 1 minuto.")