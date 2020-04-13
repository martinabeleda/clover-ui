import dataclasses
from typing import List, Union

from clover_ui.http import RequestsWithRetry


@dataclasses.dataclass(frozen=True)
class CloverAPI:
    """A wrapper class to interact with the Clover API

    Args:
        request: The Requests object
        host: The API host

    Examples:
        >>> from clover_ui.http import RequestsWithRetry, retrying_factory
        >>> request = RequestsWithRetry(retrying=retrying_factory())
        >>> clover = CloverAPI(request)
        >>> categories = clover.fetch_categories()
    """

    request: RequestsWithRetry
    host: str = "http://localhost:5000"

    def fetch_categories(self) -> Union[list, dict]:
        """Get a list of all of the existing categories"""
        url = f"{self.host}/categories"
        data = self.request.get(url=url, callback=lambda r: r.json())
        return data

    def create_category(self, name: str, display_name: str):
        """Create a new transaction category"""
        url = f"{self.host}/categories"
        payload = dict(name=name, display_name=display_name)
        data = self.request.post(url=url, json=payload, callback=lambda r: r.json())

    def fetch_transactions_by_category(self, category: str) -> list:
        """Fetch all transactions for a particular category"""
        url = f"{self.host}/categories/{category}"
        data = self.request.get(url=url, callback=lambda r: r.json())
        return data["transactions"]

    def fetch_transactions(self) -> list:
        """Fetch all transactions"""
        url = f"{self.host}/transactions"
        data = self.request.get(url=url, callback=lambda r: r.json())
        return data

    def send_transaction(
        self,
        time: str,
        transaction_type: str,
        payee: str,
        total: str,
        description: str = "",
        category_name: str = "uncategorised",
    ) -> int:
        """Create a new transaction and assign it to a category"""
        url = f"{self.host}/transactions"
        payload = dict(
            time=time,
            transaction_type=transaction_type,
            payee=payee,
            description=description,
            total=total,
            category_name=category_name,
        )
        response = self.request.post(url=url, json=payload, callback=lambda r: r.json())
        return response["id"]
