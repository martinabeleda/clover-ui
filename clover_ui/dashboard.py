from clover_ui import Facade
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

clover = Facade().configure_retry().clover()


def generate_dashboard(transactions: pd.DataFrame):

    # --- Spending by Category
    pie_figure = go.Pie(
        values=transactions.total,
        labels=transactions.display_name,
        hole=0.6,
        rotation=25,
        automargin=True,
        opacity=0.8,
        textinfo="label+value",
        textposition="outside",
        hoverlabel={"bgcolor": "rgba(255,255,255,125)"},
    )

    # https://coolors.co/browser/latest/1
    colours = [
        "#FF9B71",  # Pink-Orange
        "#2EC4B6",  # Maximum Blue-Green
        "#E84855",  # Desire
        "#E4572E",  # Flame
        "#76B041",  # Palm Leaf
        "#12355B",  # Prussian Blue
        "#2D3047",  # Gunmetal
        "#FFFD82",  # Pastel Yellow
        "#D81E5B",  # Dogwood Rose
        "#B9E3C6",  # Sea Foam Green
        "#59C9A5",  # Medium Aquamarine
    ]

    category_pie_chart = dcc.Graph(
        id="Pie",
        responsive=True,
        figure={
            "data": [pie_figure],
            "layout": go.Layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, colorway=colours
            ),
        },
    )

    category_section = dbc.Jumbotron(
        [
            html.H2("Your spending by Category"),
            html.P("See what you spent your money on this month."),
            html.Div(category_pie_chart),
        ]
    )

    # --- Daily Spend Section
    daily_expenses = transactions[transactions.total < 0].groupby("days").sum().reset_index()
    expenses_figure = go.Bar(
        x=daily_expenses.days,
        y=daily_expenses.total,
        marker_color="indianred",
        name="Expenses",
        hoverlabel={"bgcolor": "rgba(255,255,255,125)"},
    )

    daily_income = transactions[transactions.total >= 0].groupby("days").sum().reset_index()
    income_figure = go.Bar(
        x=daily_income.days,
        y=daily_income.total,
        marker_color="mediumseagreen",
        name="Income",
        hoverlabel={"bgcolor": "rgba(255,255,255,125)"},
    )

    daily_spend_chart = dcc.Graph(
        id="Bar",
        responsive=True,
        figure={
            "data": [expenses_figure, income_figure],
            "layout": go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False),
        },
    )

    daily_spend_section = html.Div(
        children=[html.Div(html.H2("Daily spend")), html.Div(daily_spend_chart)],
        style={"padding-left": "2%", "padding-right": "2%"},
    )

    return html.Div([category_section, daily_spend_section])
