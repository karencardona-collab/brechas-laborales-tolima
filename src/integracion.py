"""Etapa 4: integración demanda (SPE) + oferta (DANE) y tablas de brecha."""
import pandas as pd

_RENOMBRAR_DANE = {
    "ANIO": "ANIO_DANE",
    "Población total": "POBLACION_TOTAL_MILES",
    "Población en edad de trabajar (PET)": "PET_MILES",
    "Fuerza de trabajo": "FUERZA_TRABAJO_MILES",
    "Población ocupada": "OCUPADOS_MILES",
    "Población desocupada": "DESOCUPADOS_TOLIMA_MILES",
    "Población subocupada": "SUBOCUPADOS_TOLIMA_MILES",
    "Tasa Global de Participación (TGP)": "TGP_PCT",
    "Tasa de Ocupación (TO)": "TO_PCT",
    "Tasa de Desocupación (TD)": "TD_PCT",
}


def resumen_municipal(df_tolima):
    df = df_tolima.groupby(["DEPARTAMENTO_NORM", "MUNICIPIO_NORM"], as_index=False).agg(
        OFERTAS_PUBLICADAS=("CODIGO_VACANTE", "count"),
        VACANTES_TOTALES=("CANTIDAD_VACANTES", "sum"),
        EXPERIENCIA_PROM_MESES=("MESES_EXPERIENCIA_DEPURADOS", "mean"),
        SALARIO_PROM_COP=("SALARIO_ESTIMADO_COP", "mean"),
    )
    df["EXPERIENCIA_PROM_MESES"] = df["EXPERIENCIA_PROM_MESES"].round(1)
    df["SALARIO_PROM_COP"] = df["SALARIO_PROM_COP"].round(0)
    df["CONCENTRACION_VACANTES_PCT"] = (
        df["VACANTES_TOTALES"] / df["VACANTES_TOTALES"].sum() * 100
    ).round(2)
    return df


def integrar(df_municipal, df_dane_tabular, anio=2025):
    """Left join por DEPARTAMENTO_NORM con la línea base DANE del año indicado."""
    columnas = ["DEPARTAMENTO_NORM"] + list(_RENOMBRAR_DANE.keys())
    dane_ref = df_dane_tabular[df_dane_tabular["ANIO"] == anio][columnas].rename(
        columns=_RENOMBRAR_DANE
    )
    df = pd.merge(df_municipal, dane_ref, on="DEPARTAMENTO_NORM", how="left")
    df["DESOCUPADOS_POR_VACANTE_MUESTRA"] = (
        df["DESOCUPADOS_TOLIMA_MILES"] * 1000 / df["VACANTES_TOTALES"]
    ).round(1)
    return df


def tabla_educacion(df_tolima):
    df = df_tolima.groupby("NIVEL_ESTUDIOS", as_index=False).agg(
        OFERTAS=("CODIGO_VACANTE", "count"),
        VACANTES=("CANTIDAD_VACANTES", "sum"),
        SALARIO_PROM_COP=("SALARIO_ESTIMADO_COP", "mean"),
    ).sort_values("VACANTES", ascending=False)
    df["PARTICIPACION_PCT"] = (df["VACANTES"] / df["VACANTES"].sum() * 100).round(2)
    return df


def tabla_contrato(df_tolima):
    df = df_tolima.groupby(["TIPO_VINCULACION", "TIPO_CONTRATO"], as_index=False).agg(
        OFERTAS=("CODIGO_VACANTE", "count"),
        VACANTES=("CANTIDAD_VACANTES", "sum"),
    ).sort_values("VACANTES", ascending=False)
    df["PARTICIPACION_PCT"] = (df["VACANTES"] / df["VACANTES"].sum() * 100).round(2)
    return df
