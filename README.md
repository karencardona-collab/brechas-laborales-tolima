# Análisis de Brechas entre Oferta y Demanda Laboral en el Tolima

## Descripción del Proyecto
Pipeline de ingeniería y análisis de datos desarrollado en Python para integrar, depurar y contrastar la demanda laboral formal registrada en el Servicio Público de Empleo (Comfatolima / SPE) frente a los indicadores estructurales de oferta laboral del departamento del Tolima (DANE - GEIH, 2007–2025).

## Estructura del Repositorio
- `proyecto final.py`: Script principal del pipeline final (ETL, limpieza profunda, validaciones y generación de reportes y gráficos).
- `segundo avance.py`: Script de integración preliminar y consolidación base.
- `COMFATOLIMA (1).xlsx`: Fuente primaria de demanda laboral (vacantes publicadas en el SPE).
- `dane (1).xlsx`: Fuente primaria de oferta laboral e indicadores macroeconómicos del Tolima.
- `resultado_final_brechas_tolima.xlsx`: Dataset consolidado final generado automáticamente con 6 hojas analíticas y auditoría de calidad.
- `dashboard_brechas_tolima.png`: Tablero visual con los 4 indicadores principales de brechas laborales.

## Requisitos e Instalación
El proyecto requiere Python 3.10+ y las librerías `pandas`, `openpyxl` y `matplotlib`.

Instalación de dependencias:
```bash
pip install pandas openpyxl matplotlib
```

Ejecución del pipeline final:
```bash
python "proyecto final.py"
```

## Validaciones Implementadas
El pipeline incluye pruebas automáticas (`assert`) que garantizan:
1. Conservación del 100 % de las vacantes filtradas para el Tolima (67 puestos de trabajo).
2. Integración sin valores nulos con los indicadores departamentales del DANE.
3. Ausencia de registros duplicados y corrección de escalas atípicas tras la depuración.
