import re
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent

# ==============================================================================
# 1. CARGA DE FUENTES DE DATOS
# ==============================================================================
print("=" * 70)
print("1. CARGANDO FUENTES DE DATOS")
print("=" * 70)

archivo_vacantes = RAIZ / "data" / "raw" / "COMFATOLIMA.xlsx"
archivo_dane = RAIZ / "data" / "raw" / "dane.xlsx"

df_vacantes_raw = pd.read_excel(archivo_vacantes, sheet_name="BUE-1-20261108-0353.xlsx")
df_dane_raw = pd.read_excel(archivo_dane, sheet_name="Hoja1")

print(f"-> Fuente 1 (Vacantes SPE/Comfatolima): {df_vacantes_raw.shape[0]} filas, {df_vacantes_raw.shape[1]} columnas")
print(f"-> Fuente 2 (DANE Mercado Laboral Tolima): {df_dane_raw.shape[0]} filas, {df_dane_raw.shape[1]} columnas\n")

# ==============================================================================
# 2. DIAGNÓSTICO DE CALIDAD INICIAL
# ==============================================================================
print("=" * 70)
print("2. DIAGNÓSTICO DE CALIDAD INICIAL")
print("=" * 70)

print(f"[Vacantes] Registros duplicados exactos: {df_vacantes_raw.duplicated().sum()}")
print(f"[Vacantes] Valores nulos totales: {df_vacantes_raw.isna().sum().sum()}")
print(f"[Vacantes] Registros correspondientes a TOLIMA: {(df_vacantes_raw['DEPARTAMENTO'].str.upper().str.strip() == 'TOLIMA').sum()} de {len(df_vacantes_raw)}")
print(f"[DANE] Filas completamente vacías o de encabezado auxiliar: {df_dane_raw['Tolima'].isna().sum() + 1}")
print("[DANE] Estructura detectada: Matriz ancha (años en columnas 2007-2025) -> Requiere transposición.\n")

# ==============================================================================
# 3. TRANSFORMACIONES (6 TRANSFORMACIONES JUSTIFICADAS TÉCNICAMENTE)
# ==============================================================================
print("=" * 70)
print("3. APLICANDO TRANSFORMACIONES")
print("=" * 70)

# --- TRANSFORMACIÓN 1: Deduplicación y filtrado geográfico al departamento del Tolima ---
# Justificación: El archivo nacional contiene 1.000 ofertas y 2 duplicados; el alcance del estudio es Tolima.
df_tolima = df_vacantes_raw.drop_duplicates(subset=["CODIGO_VACANTE"]).copy()
df_tolima = df_tolima[df_tolima["DEPARTAMENTO"].str.upper().str.strip() == "TOLIMA"].copy()
print(f"T1 completada: Deduplicación y filtrado a Tolima ({len(df_tolima)} ofertas activas).")

# --- TRANSFORMACIÓN 2: Reparación de codificación (Mojibake) y limpieza de etiquetas del sistema ---
# Justificación: Textos importados en Latin-1 muestran caracteres corruptos ('ingenierÃ­a') y prefijos '$hNo Codigo vacante$'.
def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except Exception:
        pass
    texto = re.sub(r"\$hNo Codigo vacante\$", "", texto)
    return texto.strip()

cols_texto = ["TITULO_VACANTE", "SECTOR_ECONOMICO", "MUNICIPIO", "CARGO", "NOMBRE_PRESTADOR"]
for col in cols_texto:
    df_tolima[col] = df_tolima[col].apply(limpiar_texto)
print("T2 completada: Limpieza de codificación UTF-8 y eliminación de prefijos del sistema.")

# --- TRANSFORMACIÓN 3: Normalización geográfica de municipios ---
# Justificación: Homologar nombres sin tildes y en mayúsculas ('IBAGUÉ' -> 'IBAGUE') para evitar fragmentación al agrupar.
def normalizar_municipio(mun):
    mun_sin_tilde = unicodedata.normalize("NFKD", str(mun)).encode("ASCII", "ignore").decode("utf-8")
    return mun_sin_tilde.upper().strip()

df_tolima["MUNICIPIO_NORM"] = df_tolima["MUNICIPIO"].apply(normalizar_municipio)
df_tolima["DEPARTAMENTO_NORM"] = "TOLIMA"
print("T3 completada: Normalización de nombres de municipios del Tolima.")

# --- TRANSFORMACIÓN 4: Reestructuración (Transposición) de la serie histórica del DANE ---
# Justificación: Convertir la tabla matricial del DANE (2007-2025 en columnas) a formato tabular relacional (años en filas).
anios = [int(a) for a in df_dane_raw.iloc[1, 1:].tolist()]
df_dane_limpio = df_dane_raw.iloc[2:].copy()
df_dane_limpio.columns = ["CONCEPTO"] + anios
df_dane_limpio = df_dane_limpio.dropna(subset=["CONCEPTO"]).copy()
df_dane_limpio["CONCEPTO"] = df_dane_limpio["CONCEPTO"].str.strip()

df_dane_tabular = df_dane_limpio.set_index("CONCEPTO").T
df_dane_tabular.index.name = "ANIO"
df_dane_tabular = df_dane_tabular.reset_index()
df_dane_tabular["DEPARTAMENTO_NORM"] = "TOLIMA"
print(f"T4 completada: Serie DANE transformada a formato tabular ({df_dane_tabular.shape[0]} años x {df_dane_tabular.shape[1]} variables).")

# --- TRANSFORMACIÓN 5: Ingeniería de variables (Salario medio estimado y experiencia en años) ---
# Justificación: Convertir rangos salariales de texto a valor numérico medio y meses de experiencia a años para análisis cuantitativo.
def estimar_salario(rango):
    rango = str(rango)
    if "$1.500.001 - $2.000.000" in rango:
        return 1750000.0
    elif "$2.000.001 - $3.000.000" in rango:
        return 2500000.0
    elif "$3.000.001 - $4.000.000" in rango:
        return 3500000.0
    return None  # Casos 'A Convenir'

df_tolima["SALARIO_ESTIMADO_COP"] = df_tolima["RANGO_SALARIAL"].apply(estimar_salario)
df_tolima["ANIOS_EXPERIENCIA"] = (df_tolima["MESES_EXPERIENCIA_CARGO"] / 12).round(1)
print("T5 completada: Creación de variables numéricas SALARIO_ESTIMADO_COP y ANIOS_EXPERIENCIA.")

# --- TRANSFORMACIÓN 6: Agregación municipal de demanda e indicadores de brecha ---
# Justificación: Consolidar el volumen real de puestos requeridos (CANTIDAD_VACANTES) por municipio y calcular concentración.
df_demanda_municipal = df_tolima.groupby(["DEPARTAMENTO_NORM", "MUNICIPIO_NORM"], as_index=False).agg(
    TOTAL_OFERTAS=("CODIGO_VACANTE", "count"),
    TOTAL_VACANTES=("CANTIDAD_VACANTES", "sum"),
    EXPERIENCIA_PROM_MESES=("MESES_EXPERIENCIA_CARGO", "mean"),
    SALARIO_PROM_ESTIMADO=("SALARIO_ESTIMADO_COP", "mean")
)
df_demanda_municipal["EXPERIENCIA_PROM_MESES"] = df_demanda_municipal["EXPERIENCIA_PROM_MESES"].round(1)
df_demanda_municipal["SALARIO_PROM_ESTIMADO"] = df_demanda_municipal["SALARIO_PROM_ESTIMADO"].round(0)
df_demanda_municipal["PARTICIPACION_VACANTES_PCT"] = (
    df_demanda_municipal["TOTAL_VACANTES"] / df_demanda_municipal["TOTAL_VACANTES"].sum() * 100
).round(2)
print("T6 completada: Agregación de demanda laboral por municipio y peso porcentual en el departamento.\n")

# ==============================================================================
# 4. INTEGRACIÓN DE FUENTES (DEMANDA MUNICIPAL + OFERTA/CONTEXTO DANE TOLIMA)
# ==============================================================================
print("=" * 70)
print("4. INTEGRACIÓN DE DATASETS")
print("=" * 70)

# Seleccionamos el último año consolidado del DANE (2025) como línea base de oferta laboral departamental
dane_ref = df_dane_tabular[df_dane_tabular["ANIO"] == 2025][[
    "DEPARTAMENTO_NORM",
    "ANIO",
    "Población total",
    "Población en edad de trabajar (PET)",
    "Fuerza de trabajo",
    "Población ocupada",
    "Población desocupada",
    "Tasa Global de Participación (TGP)",
    "Tasa de Ocupación (TO)",
    "Tasa de Desocupación (TD)"
]].copy()

dane_ref = dane_ref.rename(columns={
    "ANIO": "ANIO_REF_DANE",
    "Población total": "POBLACION_TOTAL_MILES",
    "Población en edad de trabajar (PET)": "PET_MILES",
    "Fuerza de trabajo": "FUERZA_TRABAJO_MILES",
    "Población ocupada": "OCUPADOS_MILES",
    "Población desocupada": "DESOCUPADOS_TOLIMA_MILES",
    "Tasa Global de Participación (TGP)": "TGP_TOLIMA_PCT",
    "Tasa de Ocupación (TO)": "TO_TOLIMA_PCT",
    "Tasa de Desocupación (TD)": "TD_TOLIMA_PCT"
})

# Cruce relacional mediante la llave geográfica normalizada 'DEPARTAMENTO_NORM'
df_integrado = pd.merge(df_demanda_municipal, dane_ref, on="DEPARTAMENTO_NORM", how="left")

# Cálculo de indicador de brecha: Desocupados en el departamento por cada vacante registrada en la muestra
total_desocupados_personas = df_integrado["DESOCUPADOS_TOLIMA_MILES"] * 1000
df_integrado["PERSONAS_DESOCUPADAS_POR_VACANTE"] = (
    total_desocupados_personas / df_integrado["TOTAL_VACANTES"]
).round(1)

print("Integración exitosa por llave geográfica DEPARTAMENTO_NORM.")
print(df_integrado[["MUNICIPIO_NORM", "TOTAL_OFERTAS", "TOTAL_VACANTES", "PARTICIPACION_VACANTES_PCT", "TD_TOLIMA_PCT", "DESOCUPADOS_TOLIMA_MILES"]].to_string(index=False))
print()

# ==============================================================================
# 5. VALIDACIONES Y EXPORTACIÓN DEL DATASET CONSOLIDADO
# ==============================================================================
print("=" * 70)
print("5. VALIDACIÓN DE RESULTADOS Y EXPORTACIÓN")
print("=" * 70)

assert df_integrado["TOTAL_VACANTES"].sum() == df_tolima["CANTIDAD_VACANTES"].sum(), "Error: Pérdida de vacantes en agregación"
assert df_integrado["TD_TOLIMA_PCT"].isna().sum() == 0, "Error: Registros sin cruce con DANE"

print(f"[OK] Validación de integridad: {df_integrado['TOTAL_VACANTES'].sum()} vacantes totales conservadas sin pérdida.")
print(f"[OK] Validación de cruce: 100% de municipios cruzados con indicadores DANE ({int(df_integrado['ANIO_REF_DANE'].iloc[0])}).")
print(f"[OK] Hallazgo clave: Ibagué concentra el {df_integrado.loc[df_integrado['MUNICIPIO_NORM']=='IBAGUE', 'PARTICIPACION_VACANTES_PCT'].values[0]}% de las vacantes del Tolima.")

archivo_salida = RAIZ / "outputs" / "dataset_consolidado_brechas_tolima.xlsx"
with pd.ExcelWriter(archivo_salida, engine="openpyxl") as writer:
    df_integrado.to_excel(writer, sheet_name="1_Integrado_Brechas_Tolima", index=False)
    df_tolima.to_excel(writer, sheet_name="2_Vacantes_Tolima_Limpias", index=False)
    df_dane_tabular.to_excel(writer, sheet_name="3_Historico_DANE_2007_2025", index=False)

print(f"\nPipeline ejecutado correctamente. Archivo generado: '{archivo_salida.name}'")
