"""Etapa 5: reglas de calidad. Cada regla devuelve (nombre, aprobado)."""
from datetime import datetime

import pandas as pd


def reglas(df_integrado, df_tolima, df_dane_tabular):
    return [
        ("Integridad total de vacantes",
         df_integrado["VACANTES_TOTALES"].sum() == df_tolima["CANTIDAD_VACANTES"].sum()),
        ("Cruce 100% exitoso sin nulos DANE",
         df_integrado["TD_PCT"].isna().sum() == 0),
        ("Ausencia de duplicados en dataset limpio",
         df_tolima["CODIGO_VACANTE"].duplicated().sum() == 0),
        ("Consistencia histórica DANE (19 años: 2007-2025)",
         len(df_dane_tabular) == 19),
        ("Rango válido de tasas DANE (0% - 100%)",
         bool(df_dane_tabular["Tasa de Desocupación (TD)"].between(0, 100).all())),
    ]


def validar(df_integrado, df_tolima, df_dane_tabular):
    """Detiene la ejecución si alguna regla falla y devuelve la tabla de auditoría."""
    resultados = reglas(df_integrado, df_tolima, df_dane_tabular)
    for nombre, ok in resultados:
        assert ok, f"FALLO EN VALIDACIÓN: {nombre}"
        print(f"  [OK] {nombre}")
    df = pd.DataFrame(resultados, columns=["Regla_Validacion", "Aprobado"])
    df["Fecha_Ejecucion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df
