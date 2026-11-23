"""Etapa 3: las 5 transformaciones justificadas (ver README, sección 5)."""
import re
import unicodedata

import numpy as np
import pandas as pd

COLS_TEXTO = [
    "TITULO_VACANTE", "SECTOR_ECONOMICO", "MUNICIPIO", "CARGO",
    "NOMBRE_PRESTADOR", "NIVEL_ESTUDIOS", "TIPO_CONTRATO",
]

_REEMPLAZOS_MOJIBAKE = {
    "Ã‰": "É", "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã‘": "Ñ", "Ã\x8d": "Í", "Ã“": "Ó", "Ãš": "Ú", "Ã\x81": "Á",
}

_SALARIOS = {
    "$1.500.001 - $2.000.000": 1750000.0,
    "$2.000.001 - $3.000.000": 2500000.0,
    "$3.000.001 - $4.000.000": 3500000.0,
}


def limpiar_texto_avanzado(texto):
    """T2. Repara tildes/eñes corruptas y quita etiquetas internas del portal."""
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    for malo, bueno in _REEMPLAZOS_MOJIBAKE.items():
        texto = texto.replace(malo, bueno)
    texto = re.sub(r"\$hNo Codigo vacante\$", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_geo(texto):
    """T3. Mayúsculas y sin tildes, para usar como llave de cruce."""
    sin_tilde = unicodedata.normalize("NFKD", str(texto)).encode("ASCII", "ignore").decode("utf-8")
    return sin_tilde.upper().strip()


def estimar_salario(rango):
    """T4. Punto medio (COP) del rango salarial textual; NaN si es 'A convenir'."""
    rango = str(rango)
    for etiqueta, valor in _SALARIOS.items():
        if etiqueta in rango:
            return valor
    return np.nan


def limpiar_vacantes(df_vac_raw):
    """T1-T4 sobre la base de vacantes del SPE."""
    # T1. Deduplicación y filtro departamental
    df = df_vac_raw.drop_duplicates(subset=["CODIGO_VACANTE"]).copy()
    df = df[df["DEPARTAMENTO"].astype(str).str.upper().str.strip() == "TOLIMA"].copy()

    # T2. Saneamiento textual
    for col in COLS_TEXTO:
        df[col] = df[col].apply(limpiar_texto_avanzado)

    # T3. Llaves geográficas estandarizadas
    df["DEPARTAMENTO_NORM"] = "TOLIMA"
    df["MUNICIPIO_NORM"] = df["MUNICIPIO"].apply(normalizar_geo)

    # T4. Anomalía de escala (144 -> 12 meses), salario estimado y tipo de vinculación
    df["MESES_EXPERIENCIA_DEPURADOS"] = df["MESES_EXPERIENCIA_CARGO"].apply(
        lambda x: 12 if x == 144 else x
    )
    df["ANIOS_EXPERIENCIA"] = (df["MESES_EXPERIENCIA_DEPURADOS"] / 12).round(1)
    df["SALARIO_ESTIMADO_COP"] = df["RANGO_SALARIAL"].apply(estimar_salario)
    df["TIPO_VINCULACION"] = df["TIPO_CONTRATO"].apply(
        lambda c: "Temporal / No laboral (Obra o Prestación)"
        if c in ["Por obra o labor", "Prestación de servicios"]
        else "Directo (Fijo / Indefinido)"
    )
    return df


def limpiar_dane(df_dane_raw):
    """T5. Quita filas administrativas/nulas y transpone años a filas."""
    anios = [int(a) for a in df_dane_raw.iloc[1, 1:].tolist()]
    df = df_dane_raw.iloc[2:].copy()
    df.columns = ["CONCEPTO"] + anios
    df = df.dropna(subset=["CONCEPTO"]).copy()
    df["CONCEPTO"] = df["CONCEPTO"].str.strip()

    tabular = df.set_index("CONCEPTO").T
    tabular.index.name = "ANIO"
    tabular = tabular.reset_index()
    tabular["DEPARTAMENTO_NORM"] = "TOLIMA"
    return tabular
