import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DB_URI = os.getenv("DB_CONNECTION_STRING")

# 1. Conexión a tu base de datos v16
engine = create_engine(DB_URI)

# 2. Traer los datos limpios que ya hicimos
df = pd.read_sql('SELECT * FROM v_prestamos_limpios LIMIT 5', engine)

print("Datos cargados exitosamente:")
print(df.head())