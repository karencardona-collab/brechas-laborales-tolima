"""Punto de entrada del pipeline. Ejecutar desde la raíz del repositorio:

    python main.py
"""
from datetime import datetime

import pandas as pd

from src import config, ingesta, integracion, limpieza, validacion, visualizacion


def main():
    print("=" * 75)
    print("PIPELINE - BRECHAS LABORALES TOLIMA")
    print(f"Ejecución: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 75)

    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    config.OUTPUTS.mkdir(parents=True, exist_ok=True)

    print("\n[1/5] Cargando fuentes...")
    df_vac_raw, df_dane_raw = ingesta.cargar_fuentes()
    print(f"  -> Vacantes SPE/Comfatolima: {df_vac_raw.shape[0]} x {df_vac_raw.shape[1]}")
    print(f"  -> DANE GEIH Tolima:         {df_dane_raw.shape[0]} x {df_dane_raw.shape[1]}")

    print("\n[2/5] Diagnóstico de calidad...")
    d = ingesta.diagnostico(df_vac_raw, df_dane_raw)
    print(f"  -> Duplicados por CODIGO_VACANTE: {d['duplicados']}")
    print(f"  -> Ofertas del Tolima: {d['registros_tolima']} de {d['total_registros']}")

    print("\n[3/5] Transformaciones...")
    df_tolima = limpieza.limpiar_vacantes(df_vac_raw)
    df_dane = limpieza.limpiar_dane(df_dane_raw)
    df_tolima.to_csv(config.ARCHIVO_LIMPIO_VACANTES, index=False, encoding="utf-8-sig")
    df_dane.to_csv(config.ARCHIVO_LIMPIO_DANE, index=False, encoding="utf-8-sig")
    print("  -> 5 transformaciones ejecutadas; CSV limpios en data/processed/")

    print("\n[4/5] Integración y brechas...")
    df_integrado = integracion.integrar(integracion.resumen_municipal(df_tolima), df_dane)
    df_educacion = integracion.tabla_educacion(df_tolima)
    df_contrato = integracion.tabla_contrato(df_tolima)

    print("\n[5/5] Validaciones y entregables...")
    df_auditoria = validacion.validar(df_integrado, df_tolima, df_dane)

    with pd.ExcelWriter(config.ARCHIVO_EXCEL_FINAL, engine="openpyxl") as w:
        df_integrado.to_excel(w, sheet_name="1_Integracion_Municipal_DANE", index=False)
        df_educacion.to_excel(w, sheet_name="2_Brecha_Nivel_Educativo", index=False)
        df_contrato.to_excel(w, sheet_name="3_Brecha_Tipo_Contrato", index=False)
        df_tolima.to_excel(w, sheet_name="4_Base_Vacantes_Tolima_Limpia", index=False)
        df_dane.to_excel(w, sheet_name="5_Serie_DANE_2007_2025", index=False)
        df_auditoria.to_excel(w, sheet_name="6_Auditoria_Validaciones", index=False)

    visualizacion.generar_dashboard(df_integrado, df_educacion, df_contrato, df_dane,
                                    config.ARCHIVO_GRAFICO)

    print(f"\n[ÉXITO] Excel: {config.ARCHIVO_EXCEL_FINAL.relative_to(config.RAIZ)}")
    print(f"[ÉXITO] Gráfico: {config.ARCHIVO_GRAFICO.relative_to(config.RAIZ)}")
    print("=" * 75)


if __name__ == "__main__":
    main()
