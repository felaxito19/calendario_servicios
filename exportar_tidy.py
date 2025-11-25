import sqlite3
import pandas as pd
import os

# ============================================================
# CONFIG
# ============================================================
ruta_db = r"C:\Metso_DB_Propuestas\data\general\output_tidy.db"
carpeta_salida = "csv_export"

os.makedirs(carpeta_salida, exist_ok=True)

# ============================================================
# CONECTAR A LA BASE
# ============================================================
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = [t[0] for t in cursor.fetchall()]

reporte = []

print("\n======================================================================")
print(f"📌 Procesando base: {ruta_db}")
print("======================================================================\n")

for tabla in tablas:
    print(f"📂 Tabla: {tabla}")

    # Obtener columnas y tipos
    cursor.execute(f"PRAGMA table_info({tabla});")
    columnas_info = cursor.fetchall()

    print("   🧩 Columnas y tipos:")
    cols = []
    for col in columnas_info:
        nombre = col[1]
        tipo = col[2]
        cols.append((nombre, tipo))
        print(f"      - {nombre}: {tipo}")

    reporte.append((tabla, cols))

    # Exportar CSV
    df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
    ruta_csv = os.path.join(carpeta_salida, f"{tabla}.csv")
    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    print(f"   ✅ Exportado a: {ruta_csv}\n")

conn.close()

print("✅ FINALIZADO. Revisa la carpeta 'csv_export'.")
