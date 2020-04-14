import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


# --- Transactions
def make_transaction_group(df: pd.DataFrame):
    """Create a group of transactions"""
    list_items = []
    for idx, transaction in df.iterrows():
        list_items.append(
            dbc.ListGroupItem(
                [
                    dbc.ListGroupItemHeading(html.H6(transaction.payee)),
                    dbc.ListGroupItemText([html.P(transaction.display_name), html.P(f"$ {transaction.total}")]),
                ],
                action=True,
            )
        )
    return dbc.ListGroup(list_items)


def join_transaction_groups(transactions: pd.DataFrame):
    """Join a list of transaction groups"""
    output_list = []
    for group, df in transactions.groupby("days"):
        output_list.append(html.Div(html.H6(group.strftime("%m-%d"), style={"padding": 10})))
        output_list.append(html.Div(make_transaction_group(df), style={"padding": 10}))
    return output_list


def generate_transactions_list(transactions: pd.DataFrame):

    # --- Create list groups
    transactions_list = join_transaction_groups(transactions)

    transactions_section = html.Div(
        children=[html.Div(html.H1("Transactions")), html.Div(transactions_list),],
        style={"padding-left": "2%", "padding-right": "2%"},
    )
    return transactions_section
