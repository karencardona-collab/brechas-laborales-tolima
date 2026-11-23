"""Etapa 1 y 2: carga de las fuentes crudas y diagnóstico de calidad."""
import pandas as pd

from src import config


def cargar_fuentes():
    """Lee las dos fuentes originales sin modificarlas."""
    df_vac = pd.read_excel(config.ARCHIVO_VACANTES, sheet_name=config.HOJA_VACANTES)
    df_dane = pd.read_excel(config.ARCHIVO_DANE, sheet_name=config.HOJA_DANE)
    return df_vac, df_dane


def diagnostico(df_vac, df_dane):
    """Calcula los hallazgos de calidad iniciales y los devuelve como diccionario."""
    es_tolima = df_vac["DEPARTAMENTO"].astype(str).str.upper().str.strip() == "TOLIMA"
    return {
        "duplicados": int(df_vac.duplicated(subset=["CODIGO_VACANTE"]).sum()),
        "registros_tolima": int(es_tolima.sum()),
        "total_registros": len(df_vac),
        "filas_nulas_dane": int(df_dane["Tolima"].isna().sum()),
    }
