import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table

# =========================
# PASO 1 CARGA DE  DATOS
# =========================
df = pd.read_excel("mortalidad_2019.xlsx")

# Ajusta estos nombres según tu Excel
COL_DEP = "DEPARTAMENTO"
COL_MUN = "MUNICIPIO"
COL_MES = "MES"
COL_SEXO = "SEXO"
COL_CAUSA = "CAUSA_DEF"
COL_NOMBRE_CAUSA = "NOMBRE_CAUSA"
COL_EDAD = "GRUPO_EDAD1"

# Si cada fila representa una muerte
df["TOTAL"] = 1

# =========================
# CATEGORÍAS DE EDAD
# =========================
def clasificar_edad(codigo):
    try:
        codigo = int(codigo)
    except:
        return "Edad desconocida"

    if 0 <= codigo <= 4:
        return "Mortalidad neonatal"
    elif 5 <= codigo <= 6:
        return "Mortalidad infantil"
    elif 7 <= codigo <= 8:
        return "Primera infancia"
    elif 9 <= codigo <= 10:
        return "Niñez"
    elif codigo == 11:
        return "Adolescencia"
    elif 12 <= codigo <= 13:
        return "Juventud"
    elif 14 <= codigo <= 16:
        return "Adultez temprana"
    elif 17 <= codigo <= 19:
        return "Adultez intermedia"
    elif 20 <= codigo <= 24:
        return "Vejez"
    elif 25 <= codigo <= 28:
        return "Longevidad / Centenarios"
    else:
        return "Edad desconocida"

df["CATEGORIA_EDAD"] = df[COL_EDAD].apply(clasificar_edad)

# =========================
# GRÁFICOS
# =========================

# 1. Mapa por departamento
muertes_dep = df.groupby(COL_DEP)["TOTAL"].sum().reset_index()


fig_mapa = px.bar(
    muertes_dep,
    x=COL_DEP,
    y="TOTAL",
    title="Muertes por departamento - Colombia 2019",
    text="TOTAL"
)

fig_mapa.update_layout(
    xaxis_tickangle=-45
)

# 2. Línea por mes
muertes_mes = df.groupby(COL_MES)["TOTAL"].sum().reset_index()

fig_linea = px.line(
    muertes_mes,
    x=COL_MES,
    y="TOTAL",
    markers=True,
    title="Total de muertes por mes en Colombia - 2019"
)

# 3. Top 5 ciudades más violentas por homicidios X95
df_homicidios = df[df[COL_CAUSA].astype(str).str.contains("X95", na=False)]

top_violentas = (
    df_homicidios.groupby(COL_MUN)["TOTAL"]
    .sum()
    .reset_index()
    .sort_values("TOTAL", ascending=False)
    .head(5)
)

fig_barras = px.bar(
    top_violentas,
    x=COL_MUN,
    y="TOTAL",
    title="Top 5 ciudades más violentas por homicidios X95",
    text="TOTAL"
)

# 4. Gráfico circular: 10 ciudades con menor mortalidad
menor_mortalidad = (
    df.groupby(COL_MUN)["TOTAL"]
    .sum()
    .reset_index()
    .sort_values("TOTAL", ascending=True)
    .head(10)
)

fig_pie = px.pie(
    menor_mortalidad,
    names=COL_MUN,
    values="TOTAL",
    title="10 ciudades con menor índice de mortalidad"
)

# 5. Tabla principales causas
top_causas = (
    df.groupby([COL_CAUSA, COL_NOMBRE_CAUSA])["TOTAL"]
    .sum()
    .reset_index()
    .sort_values("TOTAL", ascending=False)
    .head(10)
)

# 6. Barras apiladas por sexo y departamento
sexo_dep = (
    df.groupby([COL_DEP, COL_SEXO])["TOTAL"]
    .sum()
    .reset_index()
)

fig_apiladas = px.bar(
    sexo_dep,
    x=COL_DEP,
    y="TOTAL",
    color=COL_SEXO,
    title="Muertes por sexo en cada departamento",
    barmode="stack"
)

# 7. Histograma por categoría de edad
edad_categoria = (
    df.groupby("CATEGORIA_EDAD")["TOTAL"]
    .sum()
    .reset_index()
)

fig_histograma = px.bar(
    edad_categoria,
    x="CATEGORIA_EDAD",
    y="TOTAL",
    title="Distribución de muertes por grupo de edad",
    text="TOTAL"
)

# =========================
# APP DASH
# =========================
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Dashboard de Mortalidad en Colombia - 2019",
            style={"textAlign": "center"}),

    html.P(
        "Aplicación web dinámica desarrollada con Python, Dash y Plotly.",
        style={"textAlign": "center"}
    ),

    dcc.Graph(figure=fig_mapa),
    dcc.Graph(figure=fig_linea),
    dcc.Graph(figure=fig_barras),
    dcc.Graph(figure=fig_pie),

    html.H2("10 principales causas de muerte en Colombia"),
    dash_table.DataTable(
        data=top_causas.to_dict("records"),
        columns=[
            {"name": "Código", "id": COL_CAUSA},
            {"name": "Causa de muerte", "id": COL_NOMBRE_CAUSA},
            {"name": "Total casos", "id": "TOTAL"},
        ],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "8px"},
        style_header={"fontWeight": "bold"}
    ),

    dcc.Graph(figure=fig_apiladas),
    dcc.Graph(figure=fig_histograma),
])

if __name__ == "__main__":
    app.run(debug=True)