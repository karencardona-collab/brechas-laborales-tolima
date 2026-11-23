# Fuentes de datos

| Archivo | Entidad | Hoja leída | Tamaño crudo |
|---|---|---|---|
| `data/raw/COMFATOLIMA.xlsx` | Servicio Público de Empleo (SPE) / Comfatolima — ofertas publicadas, corte 2026 | `BUE-1-20261108-0353.xlsx` | 1.000 filas × 20 columnas |
| `data/raw/dane.xlsx` | DANE — Gran Encuesta Integrada de Hogares (GEIH), Tolima 2007-2025 | `Hoja1` | 16 filas × 20 columnas |

Los archivos de `data/raw/` son los originales y no se modifican: el pipeline los lee y escribe sus resultados en `data/processed/` y `outputs/`.

Los archivos se renombraron respecto a la versión anterior del repositorio (`COMFATOLIMA (1).xlsx` y `dane (1).xlsx`) para evitar espacios y paréntesis en las rutas.
