import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime

# Исправленные данные (все массивы одинаковой длины)
date_range = pd.date_range(start="2024-07-01", end="2024-11-30", freq="D").tolist()
num_days = len(date_range)

data = {
    "Дата": date_range * 2,  # Удвоим для одинаковой длины
    "Номенклатурная группа": ["Стрелки", "Ремкомплекты", "Крестовины"] * (num_days * 2 // 3),  # 366 * 2 / 3 = 244
    "Цех": ["Механо-сборочный", "Механо-изготовительный"] * (num_days),  # 366 * 2 / 2 = 366
    "План": [100, 150, 200] * (num_days * 2 // 3),  # 366 * 2 / 3 = 244
    "Факт": [90, 140, 190] * (num_days * 2 // 3),  # 366 * 2 / 3 = 244
    "Проект": ["Проект A", "Проект B", "Проект C"] * (num_days * 2 // 3),  # 366 * 2 / 3 = 244
    "Рынок": ["РЖД", "Прочий рынок"] * (num_days),  # 366 * 2 / 2 = 366
}

# Создание DataFrame
df = pd.DataFrame(data)

# Проверка длин массивов
for key, value in data.items():
    print(f"{key}: {len(value)}")

# Инициализация приложения Dash
app = dash.Dash(__name__)
server = app.server  # Для развертывания на Render

# Макет дашборда
app.layout = html.Div([
    # Заголовок
    html.H1("Дашборд для анализа производства", style={"textAlign": "center"}),

    # Фильтры
    html.Div([
        html.Label("Выберите период:"),
        dcc.DatePickerRange(
            id="date-range",
            start_date=df["Дата"].min(),
            end_date=df["Дата"].max(),
            display_format="YYYY-MM-DD"
        ),
        html.Label("Выберите номенклатурную группу:"),
        dcc.Dropdown(
            id="nomenclature-dropdown",
            options=[{"label": i, "value": i} for i in df["Номенклатурная группа"].unique()],
            value=df["Номенклатурная группа"].unique(),
            multi=True
        ),
        html.Label("Выберите цех:"),
        dcc.Dropdown(
            id="workshop-dropdown",
            options=[{"label": i, "value": i} for i in df["Цех"].unique()],
            value=df["Цех"].unique(),
            multi=True
        ),
    ], style={"margin": "20px"}),

    # Графики и диаграммы
    html.Div([
        # Линейный график динамики плана и факта
        dcc.Graph(id="line-chart"),
        # Круговая диаграмма долей продукции
        dcc.Graph(id="pie-chart"),
        # Сводная таблица
        html.Div(id="summary-table")
    ]),
])

# Callback для обновления графиков
@app.callback(
    [Output("line-chart", "figure"),
     Output("pie-chart", "figure"),
     Output("summary-table", "children")],
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("nomenclature-dropdown", "value"),
     Input("workshop-dropdown", "value")]
)
def update_dashboard(start_date, end_date, nomenclature, workshop):
    # Фильтрация данных
    filtered_df = df[
        (df["Дата"] >= start_date) &
        (df["Дата"] <= end_date) &
        (df["Номенклатурная группа"].isin(nomenclature)) &
        (df["Цех"].isin(workshop))
    ]

    # Линейный график
    line_fig = px.line(
        filtered_df,
        x="Дата",
        y=["План", "Факт"],
        title="Динамика плана и факта",
        labels={"value": "Количество", "variable": "Показатель"}
    )

    # Круговая диаграмма
    pie_fig = px.pie(
        filtered_df,
        names="Номенклатурная группа",
        values="Факт",
        title="Доля продукции по номенклатурным группам"
    )

    # Сводная таблица
    summary_table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in ["Показатель", "Значение"]])),
        html.Tbody([
            html.Tr([html.Td("Общий план"), html.Td(filtered_df["План"].sum())]),
            html.Tr([html.Td("Общий факт"), html.Td(filtered_df["Факт"].sum())]),
            html.Tr([html.Td("Отклонение"), html.Td(filtered_df["План"].sum() - filtered_df["Факт"].sum())]),
        ])
    ])

    return line_fig, pie_fig, summary_table

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)