"""A helper script to populate the API with data from files
"""
import argparse
import json
import logging
from pathlib import Path

from clover_ui import Facade
from clover_ui.log import configure_parent_logger
import pandas as pd

logger = configure_parent_logger(level=logging.INFO)

clover = Facade().configure_retry().clover()


def get_categories(search_path: Path) -> dict:
    """Load in our mappings for categories to category names"""
    categories_path = search_path / "categories.json"
    with categories_path.open("r") as f:
        categories = json.load(f)
    logger.info(f"Found: {len(categories)} categories.")
    return categories


def create_categories(categories: dict):
    """Ensure all our categories exist in the API"""
    for display_name, name in categories.items():
        try:
            response = clover.fetch_transactions_by_category(name)
        except FileNotFoundError:
            logger.info(f"Category: ({display_name}, {name}) doesn't exist, creating")
            clover.create_category(name, display_name)


def load_csvs(search_path: Path) -> pd.DataFrame:
    """Load a bunch of CSVs in a search path into a `pandas.DataFrame`."""
    data = []
    for file in search_path.glob("*.csv"):
        data.append(pd.read_csv(file))
    return pd.concat(data).fillna("").reset_index(drop=True)


def create_transactions(transactions: pd.DataFrame, categories: dict):

    transactions["Total (AUD)"] = (
        transactions["Total (AUD)"].str.replace(",", "").astype(float)
    )

    for index, transaction in transactions.iterrows():
        transaction_id = clover.send_transaction(
            time=transaction["Time"],
            transaction_type=transaction["Transaction Type"],
            payee=transaction["Payee"],
            description=transaction["Description"],
            total=float(transaction["Total (AUD)"]),
            category_name=categories.get(transaction["Category"], "uncategorised"),
        )
        logger.info(
            f"Created transaction {index} of {transactions.shape[0]}... ID: {transaction_id}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script takes a directory of transaction CSVs and posts them to the Clover API"
    )
    parser.add_argument(
        "search_path",
        help="Path to dircetory containing CSV files to load and post",
        type=Path,
    )
    args = parser.parse_args()
    categories = get_categories(args.search_path)
    create_categories(categories)
    transactions = load_csvs(args.search_path)
    create_transactions(transactions, categories)
