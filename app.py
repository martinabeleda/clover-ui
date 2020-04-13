from clover_ui import Facade
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

clover = Facade().configure_retry().clover()
transactions = clover.fetch_transactions()
transactions = pd.DataFrame(transactions)
transactions = transactions.loc[transactions.category_name != "uncategorised"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

navbar = dbc.NavbarSimple(brand="Clover")

content = html.Div(
    [
        html.Div(html.H1("Spending")),
        html.Div(
            dcc.Graph(
                id="Pie",
                figure=dict(
                    data=[
                        go.Pie(
                            values=transactions.total,
                            labels=transactions.category_name,
                            hole=0.7,
                            rotation=25,
                            opacity=0.8,
                        )
                    ],
                    layout=dict(title="By Category", showlegend=False),
                ),
            )
        ),
    ]
)

app.layout = html.Div([dcc.Location(id="url"), navbar, content])

if __name__ == "__main__":
    app.run_server(debug=True)
