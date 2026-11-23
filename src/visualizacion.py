"""Dashboard de 4 gráficos para la sustentación."""
import matplotlib

matplotlib.use("Agg")  # sin ventana: funciona en servidores y en Colab
import matplotlib.pyplot as plt


def generar_dashboard(df_integrado, df_educacion, df_contrato, df_dane_tabular, ruta):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Análisis de Brechas entre Oferta y Demanda Laboral - Departamento del Tolima",
                 fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(df_dane_tabular["ANIO"], df_dane_tabular["Tasa de Ocupación (TO)"],
            marker="o", color="#1f77b4", label="Tasa de Ocupación (%)")
    ax.plot(df_dane_tabular["ANIO"], df_dane_tabular["Tasa de Desocupación (TD)"],
            marker="s", color="#d62728", label="Tasa de Desocupación (%)")
    ax.set_title("1. Oferta Laboral: Evolución TD y TO en Tolima (DANE 2007-2025)",
                 fontweight="bold", fontsize=10)
    ax.set_xlabel("Año")
    ax.set_ylabel("Porcentaje (%)")
    ax.legend()

    total = int(df_integrado["VACANTES_TOTALES"].sum())
    ax = axes[0, 1]
    d = df_integrado.sort_values("VACANTES_TOTALES", ascending=True)
    barras = ax.barh(d["MUNICIPIO_NORM"], d["VACANTES_TOTALES"], color="#2ca02c")
    ax.set_title(f"2. Brecha Geográfica: Vacantes por Municipio (Total = {total})",
                 fontweight="bold", fontsize=10)
    ax.set_xlabel("Cantidad de Vacantes")
    for b in barras:
        ax.text(b.get_width() + 0.8, b.get_y() + b.get_height() / 2,
                f"{int(b.get_width())}", va="center", fontweight="bold")

    ax = axes[1, 0]
    d = df_educacion.sort_values("VACANTES", ascending=True)
    barras = ax.barh(d["NIVEL_ESTUDIOS"], d["VACANTES"], color="#9467bd")
    ax.set_title("3. Brecha Formativa: Vacantes por Nivel Educativo", fontweight="bold", fontsize=10)
    ax.set_xlabel("Cantidad de Vacantes")
    for b in barras:
        ax.text(b.get_width() + 0.5, b.get_y() + b.get_height() / 2,
                f"{int(b.get_width())}", va="center", fontweight="bold")

    ax = axes[1, 1]
    colores = ["#ff7f0e", "#ffbb78", "#17becf", "#9edae5"][: len(df_contrato)]
    barras = ax.bar(df_contrato["TIPO_CONTRATO"], df_contrato["VACANTES"], color=colores)
    ax.set_title("4. Brecha de Estabilidad: Vacantes por Tipo de Contrato",
                 fontweight="bold", fontsize=10)
    ax.set_ylabel("Cantidad de Vacantes")
    ax.tick_params(axis="x", rotation=15)
    for b in barras:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                f"{int(b.get_height())}", ha="center", fontweight="bold")

    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    plt.savefig(ruta, dpi=300)
    plt.close(fig)
