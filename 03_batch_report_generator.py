import pandas as pd
from sqlalchemy import create_engine
from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
MODELO = "gemini-2.5-flash"

if not os.path.exists('Reportes_Clientes'):
    os.makedirs('Reportes_Clientes')
    print("📁 Carpeta 'Reportes_Clientes' creada o existente.")

engine = create_engine(DB_URI)

print(" Extrayendo 10 casos aleatorios de la base de datos...")
query = "SELECT * FROM v_prestamos_limpios ORDER BY RANDOM() LIMIT 10"
df = pd.read_sql(query, engine)

print(f" Iniciando generación masiva para {len(df)} clientes...\n")

for index, row in df.iterrows():
    id_corto = row['id_cliente_anonimizado'][:8] 
    print(f" Procesando Cliente {index+1}/10: [ID: {id_corto}...] ", end="", flush=True)

    prompt = f"""
        Actúa como un Senior Risk Officer de un banco en Colombia. 
        Analiza este caso y genera un reporte ejecutivo de 2 párrafos.
        Los montos están expresados en PESOS COLOMBIANOS (COP).
        
        DATOS:
        - ID: {row['id_cliente_anonimizado']}
        - Depto: {row['departamento']}
        - Ingresos: ${row['ingresos_anuales_cop']:,} COP
        - Monto: ${row['monto_prestamo_cop']:,} COP
        - Motivo: {row['motivo_prestamo']}
        - Riesgo: {row['categoria_riesgo']}
        - Estado: {row['estado_pago']}
        - Fecha: {row['fecha_desembolso']}
        """

    try:
        response = client.models.generate_content(model=MODELO, contents=prompt)
        reporte_texto = response.text

        nombre_archivo = f"Reportes_Clientes/Reporte_{id_corto}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(f"REPORTE DE RIESGO IA - BANCO COLOMBIA 2026\n")
            f.write("="*50 + "\n")
            f.write(reporte_texto)
        
        print(" Guardado.")
        time.sleep(30)

    except Exception as e:
        print(f" Error: {e}")

print(" ¡Proceso completado! Revisa la carpeta 'Reportes_Clientes'.")