# Análisis de Brechas entre Oferta y Demanda Laboral en el Tolima
**Pipeline reproducible de integración y transformación de datos**[cite: 9]

* **Asignatura:** Fundamentos de Integración y Transformación de Datos — Universidad de Ibagué (2026)[cite: 9]
* **Docente:** Mariana Millán Meneses[cite: 9]
* **Integrantes:** Karen Vanesa Cardona, María Fernanda Rodríguez, Karen Natalia Moreno Bermúdez[cite: 9]

> Con un solo comando (`python "proyecto final.py"`) el pipeline lee las fuentes crudas, las diagnostica, las limpia con cinco transformaciones justificadas, las integra en un único dataset, valida el resultado y genera un reporte de calidad y visualización[cite: 9].

---

## 1. Problema y objetivo
En el departamento del Tolima existe una desarticulación estructural entre la oferta laboral disponible (personas que buscan empleo) y la demanda formal publicada por las empresas. El análisis aislado de las vacantes o de las encuestas de hogares impide identificar con precisión dónde se concentran las barreras de absorción del desempleo.

* **Objetivo general:** Integrar, depurar y contrastar las fuentes oficiales de oferta y demanda laboral del Tolima mediante un pipeline reproducible en Python para diagnosticar brechas geográficas, educativas y contractuales.
* **Objetivos específicos:**
  1. Diagnosticar problemas de calidad, codificación y estructura en las bases crudas de vacantes y encuestas de hogares.
  2. Aplicar transformaciones documentadas para homologar llaves geográficas, corregir escalas atípicas y normalizar formatos.
  3. Integrar relacionalmente la demanda municipal de empleo con los indicadores macroeconómicos del Tolima y validar automáticamente la consistencia del dataset resultante.

---

## 2. Fuentes de datos
| Fuente | Archivo en repositorio | Entidad / Origen | Granularidad y cobertura | Registros crudos |
| :--- | :--- | :--- | :--- | :--- |
| **Demanda laboral** | `COMFATOLIMA (1).xlsx` | Servicio Público de Empleo (SPE) / Comfatolima | Ofertas laborales publicadas (corte 2026) | 1.000 filas × 26 variables |
| **Oferta laboral** | `dane (1).xlsx` | DANE — Gran Encuesta Integrada de Hogares (GEIH) | Indicadores anuales departamentales del Tolima (2007–2025) | 12 filas × 20 columnas |

---

## 3. Arquitectura del pipeline
El flujo de procesamiento sigue una arquitectura ETL secuencial y reproducible con rutas relativas:

```text
[COMFATOLIMA (1).xlsx] ──┐
                         ├──> (1) Ingesta y Diagnóstico ──> (2) 5 Transformaciones ──> (3) Integración Relacional
[dane (1).xlsx] ─────────┘                                                                       │
                                                                                                 ▼
[dashboard_brechas_tolima.png] + [resultado_final_brechas_tolima.xlsx] <── (4) Validaciones (assert)
```

---

## 4. Diagnóstico de calidad (evidencia inicial)
Al auditar las fuentes originales se identificaron los siguientes hallazgos:
1. **Duplicidad y alcance geográfico:** La base del SPE contiene 1.000 registros nacionales con **2 códigos de vacante duplicados** y solo **11 ofertas** (equivalentes a **67 puestos de trabajo**) pertenecientes al departamento del Tolima.
2. **Corrupción de caracteres (Mojibake) y etiquetas internas:** Títulos y sectores presentaban errores de codificación UTF-8/Latin-1 (ej. `AUXILIAR DE BODEGA/ALMACÃ‰N`) y cadenas residuales del portal (`$hNo Codigo vacante$`).
3. **Inconsistencia de llaves geográficas:** Nombres de municipios con y sin tildes (`Ibagué` vs `Ibague`) que impiden cruces exactos.
4. **Valores atípicos de escala:** Dos ofertas operativas registraban `144` meses de experiencia (12 años) debido a un error de multiplicación (`12 × 12`) en la captura del formulario, contradiciendo la descripción del cargo.
5. **Estructura no tabular del DANE:** La hoja del DANE presenta filas de encabezado administrativo, **1 fila separadora completamente nula** y años dispuestos horizontalmente (2007–2025) en lugar de filas observacionales.

---

## 5. Transformaciones (5) y su justificación
1. **Deduplicación y filtrado departamental (`drop_duplicates` + filtro `TOLIMA`):** Elimina registros repetidos por `CODIGO_VACANTE` y acota la demanda al ámbito territorial del estudio (11 ofertas / 67 vacantes).
2. **Saneamiento textual y reparación de codificación (`limpiar_texto_avanzado`):** Restaura tildes y eñes corruptas (`ALMACÃ‰N` $\rightarrow$ `ALMACÉN`), elimina etiquetas internas del sistema y normaliza espacios múltiples.
3. **Estandarización geográfica (`unicodedata.normalize`):** Genera las llaves limpias `DEPARTAMENTO_NORM` (`TOLIMA`) y `MUNICIPIO_NORM` en mayúsculas y sin diacríticos (`IBAGUE`, `ESPINAL`, `HONDA`, `MELGAR`) para garantizar integridad referencial.
4. **Corrección de anomalías numéricas y enriquecimiento de variables:** Corrige el error de escala de experiencia (`144` $\rightarrow$ `12` meses), estima el salario promedio numérico en COP a partir de los rangos textuales y clasifica la estabilidad contractual (`Temporal / No laboral` vs `Directo`).
5. **Transposición y limpieza estructural de la serie DANE:** Elimina filas administrativas y nulas, y transpone la matriz de indicadores (2007–2025) a un formato tabular limpio indexado por año y departamento.

---

## 6. Integración
La integración se realiza mediante un cruce relacional (`pd.merge` tipo `left`) utilizando la llave estandarizada `DEPARTAMENTO_NORM = "TOLIMA"`:
* **Tabla izquierda (Demanda agregada):** Resumen municipal de vacantes, experiencia promedio y salario estimado del SPE (2026).
* **Tabla derecha (Oferta estructural):** Línea base macroeconómica más reciente del DANE para el Tolima (2025: Población desocupada, Fuerza de trabajo, TGP, TO y TD).
* **Métrica derivada:** Se calcula la razón `DESOCUPADOS_POR_VACANTE_MUESTRA` para dimensionar la presión de oferta laboral frente a la capacidad de absorción formal en cada municipio.

---

## 7. Validaciones
Antes de exportar los resultados, el pipeline ejecuta reglas de control de calidad sobre el dataset integrado:
* **Integridad de volumen:** Verifica que la suma de vacantes municipales tras la agregación coincida exactamente con el total depurado (`67` puestos).
* **Completitud del cruce:** Comprueba `0` valores nulos en los indicadores macroeconómicos anexados del DANE.
* **Unicidad:** Verifica ausencia de duplicados en `CODIGO_VACANTE` y cobertura completa de los 19 años históricos (2007–2025).
* **Consistencia de dominio:** Valida que las tasas porcentuales del DANE (TGP, TO, TD) se encuentren estrictamente en el rango `[0, 100]`.

---

## 8. Cómo ejecutar
### Requisitos
* Python 3.10 o superior
* Dependencias: `pandas`, `openpyxl`, `matplotlib`

### Pasos de ejecución
1. Clonar o descargar este repositorio asegurando que los archivos `.py` y `.xlsx` permanezcan en la misma carpeta raíz.
2. Instalar las librerías necesarias:
   ```bash
   pip install pandas openpyxl matplotlib
   ```
3. Ejecutar el pipeline principal:
   ```bash
   python "proyecto final.py"
   ```
   *(Alternativamente, si se utiliza `uv`: `uv run --with pandas --with openpyxl --with matplotlib python "proyecto final.py"`)*

---

## 9. Pruebas automáticas
El script incorpora aserciones automáticas (`assert`) en la **Etapa 5** que detienen la ejecución con un mensaje explícito si alguna regla de negocio o calidad falla:
```python
assert df_integrado["VACANTES_TOTALES"].sum() == df_tolima["CANTIDAD_VACANTES"].sum()
assert df_integrado["TD_PCT"].isna().sum() == 0
assert df_tolima["CODIGO_VACANTE"].duplicated().sum() == 0
assert len(df_dane_tabular) == 19
assert df_dane_tabular["Tasa de Desocupación (TD)"].between(0, 100).all()
```
El resultado de cada verificación queda registrado con marca de tiempo en la hoja `6_Auditoria_Validaciones` del Excel de salida.

---

## 10. Estructura del repositorio
```text
brechas-laborales-tolima/
├── COMFATOLIMA (1).xlsx                        # Fuente cruda: vacantes SPE / Comfatolima
├── dane (1).xlsx                               # Fuente cruda: indicadores GEIH Tolima (2007-2025)
├── segundo avance.py                           # Script de integración preliminar (Avance 2)
├── proyecto final.py                           # Pipeline final completo, validaciones y gráficos
├── conjunto de datos_consolidado_brechas_tolima.xlsx # Salida intermedia del Avance 2
├── resultado_final_brechas_tolima.xlsx         # Entregable final en Excel (6 hojas analíticas)
├── dashboard_brechas_tolima.png                # Tablero visual de 4 gráficos generado automáticamente
└── README.md                                   # Documentación técnica del proyecto
```

---

## 11. Limitaciones y decisiones de diseño
* **Diferencia de temporalidad y granularidad:** Las cifras del DANE tienen corte anual departamental (último cierre consolidado 2025), mientras que las vacantes del SPE representan una muestra puntual (2026) con desagregación municipal. Se decidió integrar a nivel departamental (`TOLIMA`) como contexto estructural sin imputar artificialmente tasas de desempleo municipales inexistentes en la GEIH.
* **Rutas relativas:** Se optó por rutas relativas en la raíz del proyecto para garantizar portabilidad total entre sistemas operativos sin modificar el código.
* **Estimación salarial:** Dado que el SPE publica rangos salariales en texto, se calculó el punto medio del intervalo en pesos colombianos para habilitar promedios cuantitativos, manteniendo como `NaN` los registros sin rango declarado.

---

## 12. Resultados de la ejecución con los datos reales
Al ejecutar `proyecto final.py` sobre las bases reales se obtienen los siguientes hallazgos principales:
1. **Contexto de oferta laboral (DANE 2025):** El Tolima registra una Fuerza de Trabajo de **669.547 personas**, una población desocupada de **72.457 personas** y una Tasa de Desocupación (TD) de **10,82 %** (frente al pico pandémico de 23,24 % en 2020).
2. **Brecha geográfica:** **Ibagué concentra el 89,55 %** de la demanda formal (60 de 67 vacantes), seguida a gran distancia por Espinal (5,97 %, 4 vacantes), Honda (2,99 %, 2 vacantes) y Melgar (1,49 %, 1 vacante).
3. **Brecha educativa:** El **77,61 %** de los puestos solicitados exige formación **Media (49,25 %)** o **Técnica (28,36 %)**, mientras que el nivel **Universitario apenas alcanza el 2,99 %** (2 vacantes).
4. **Brecha de estabilidad contractual:** El **97,01 %** de las vacantes (65 de 67) corresponde a vinculaciones temporales o no laborales (*Por obra o labor*: 59,70 %; *Prestación de servicios*: 37,31 %), frente a solo un **2,99 %** de contratación directa (fijo o indefinido).

---

## 13. Participación del equipo
El proyecto fue desarrollado colaborativamente por las tres integrantes[cite: 10]:

| Integrante | Cuenta de GitHub | Aporte |
| :--- | :--- | :--- |
| **Karen Natalia Moreno Bermúdez** | `karenmoreno1805` | Organización del repositorio, ejecución del pipeline, generación de entregables y documentación[cite: 8, 10] |
| **María Fernanda Rodríguez** | `mariarodriguez22-hub` | Desarrollo de transformaciones, análisis de calidad y aportes registrados en el historial del proyecto[cite: 10] |
| **Karen Vanesa Cardona** | `karencardona-collab` | Coautora del diagnóstico inicial, diseño metodológico, pruebas y sustentación[cite: 8, 10] |

---

## 14. Historial del proyecto
* **Avance 1:** Definición del problema, extracción inicial de las bases del SPE y DANE, diccionario de variables y diagnóstico preliminar de calidad[cite: 10].
* **Avance 2 (`segundo avance.py`):** Implementación de limpieza inicial, normalización geográfica y primera consolidación en `conjunto de datos_consolidado_brechas_tolima.xlsx`[cite: 10].
* **Versión final (`proyecto final.py`):** Incorporación de las 5 transformaciones justificadas, corrección de anomalías de escala y codificación, pruebas automáticas (`assert`), tablero gráfico (`dashboard_brechas_tolima.png`) y reporte consolidado de 6 hojas (`resultado_final_brechas_tolima.xlsx`)[cite: 10].
