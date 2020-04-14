from clover_ui import Facade
from clover_ui.dashboard import generate_dashboard
from clover_ui.transactions import generate_transactions_list
import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

clover = Facade().configure_retry().clover()

categories = clover.fetch_categories()
categories = pd.DataFrame(categories)

transactions = clover.fetch_transactions()
transactions = pd.DataFrame(transactions)
transactions = transactions.loc[transactions.category_name != "uncategorised"]
transactions = transactions.merge(categories, how="left", left_on="category_name", right_on="name")
transactions.index = pd.to_datetime(transactions.time)
transactions["days"] = transactions.index.floor("d")

app = dash.Dash(external_stylesheets=[dbc.themes.LITERA])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


FILTERBAR_STYLE = {}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "24rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


elements = [
    dbc.Label("By month", style={"padding-top": "1cm"}),
]
for year, year_df in transactions.groupby(pd.Grouper(freq="YS")):
    elements.append(html.P(year.year, className="lead", style={"padding-top": "0.5cm"}))
    for month, month_df in year_df.groupby(pd.Grouper(freq="M")):
        elements.append(dbc.Button(month.month_name(), color="light", id=f"{month.month_name()}-{year.year}"))

switches = dbc.FormGroup(
    [
        dbc.Label("By transaction type"),
        dbc.Checklist(options=[{"label": "Show transfers", "value": 1},], value=[], id="switches-input", switch=True,),
    ]
)


sidebar = html.Div(
    [
        html.H1("Clover"),
        html.P("A budgeting app that keeps it simple", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/page-1", id="page-1-link"),
                dbc.NavLink("Transactions", href="/page-2", id="page-2-link"),
                dbc.NavLink("Categories", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
        html.H4("Filter", style={"padding-top": "3cm"}),
        switches,
        html.Div(elements),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)], [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return generate_dashboard(transactions)
    elif pathname == "/page-2":
        return generate_transactions_list(transactions)
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
