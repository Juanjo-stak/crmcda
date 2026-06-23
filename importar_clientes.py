import pandas as pd
from supabase_config import supabase

ARCHIVO = "clientes.xlsx"

dsupabase.table("clientes").update(...)

for _, row in df.head(10).iterrows():

    fecha = pd.to_datetime(
        row["Fecha"],
        dayfirst=True,
        errors="coerce"
    )

    datos = {
        "placa": str(row["Placa"]).strip(),
        "cliente": str(row["Cliente"]).strip(),
        "telefono": str(row["Telefono"]).strip(),
        "sede": str(row["Sede"]).strip(),
        "fecha_renovacion": fecha.strftime("%Y-%m-%d"),
        "estado": str(row["Estado"]).strip()
    }

    supabase.table("clientes").insert(datos).execute()

print("Importación completada")