"""Pruebas del pipeline. Ejecutar desde la raíz:  pytest -q"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import ingesta, integracion, limpieza, validacion  # noqa: E402


@pytest.fixture(scope="module")
def datos():
    df_vac_raw, df_dane_raw = ingesta.cargar_fuentes()
    df_tolima = limpieza.limpiar_vacantes(df_vac_raw)
    df_dane = limpieza.limpiar_dane(df_dane_raw)
    df_int = integracion.integrar(integracion.resumen_municipal(df_tolima), df_dane)
    return df_vac_raw, df_tolima, df_dane, df_int


def test_normalizar_geo():
    assert limpieza.normalizar_geo("Ibagué") == "IBAGUE"
    assert limpieza.normalizar_geo(" Espinal ") == "ESPINAL"


def test_limpiar_texto_quita_etiqueta_y_repara_mojibake():
    assert limpieza.limpiar_texto_avanzado("ALMACÃ‰N $hNo Codigo vacante$") == "ALMACÉN"
    assert limpieza.limpiar_texto_avanzado(None) == ""


def test_estimar_salario():
    assert limpieza.estimar_salario("$2.000.001 - $3.000.000") == 2500000.0
    assert pd.isna(limpieza.estimar_salario("A Convenir"))


def test_sin_duplicados_y_solo_tolima(datos):
    _, df_tolima, _, _ = datos
    assert not df_tolima["CODIGO_VACANTE"].duplicated().any()
    assert (df_tolima["DEPARTAMENTO_NORM"] == "TOLIMA").all()


def test_anomalia_144_corregida(datos):
    _, df_tolima, _, _ = datos
    assert (df_tolima["MESES_EXPERIENCIA_DEPURADOS"] != 144).all()


def test_serie_dane_19_anios(datos):
    _, _, df_dane, _ = datos
    assert len(df_dane) == 19
    assert df_dane["Tasa de Desocupación (TD)"].between(0, 100).all()


def test_integracion_conserva_vacantes_y_cruza_dane(datos):
    _, df_tolima, _, df_int = datos
    assert df_int["VACANTES_TOTALES"].sum() == df_tolima["CANTIDAD_VACANTES"].sum()
    assert df_int["TD_PCT"].notna().all()


def test_todas_las_reglas_de_validacion_pasan(datos):
    _, df_tolima, df_dane, df_int = datos
    assert all(ok for _, ok in validacion.reglas(df_int, df_tolima, df_dane))
