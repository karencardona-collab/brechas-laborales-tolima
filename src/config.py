"""Rutas y constantes del proyecto (todas relativas a la raíz del repositorio)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"
OUTPUTS = RAIZ / "outputs"

ARCHIVO_VACANTES = DATA_RAW / "COMFATOLIMA.xlsx"
HOJA_VACANTES = "BUE-1-20261108-0353.xlsx"
ARCHIVO_DANE = DATA_RAW / "dane.xlsx"
HOJA_DANE = "Hoja1"

ARCHIVO_EXCEL_FINAL = OUTPUTS / "resultado_final_brechas_tolima.xlsx"
ARCHIVO_GRAFICO = OUTPUTS / "dashboard_brechas_tolima.png"
ARCHIVO_LIMPIO_VACANTES = DATA_PROCESSED / "vacantes_tolima_limpias.csv"
ARCHIVO_LIMPIO_DANE = DATA_PROCESSED / "dane_tolima_2007_2025.csv"
