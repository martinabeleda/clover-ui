import dataclasses

from clover_ui.api import CloverAPI
from clover_ui.http import RequestsWithRetry, retrying_factory


@dataclasses.dataclass(frozen=False)
class Facade:
    """A facade used for creating classes that interact with Nearmap's public APIs"""

    request: RequestsWithRetry = dataclasses.field(init=False)

    def __post_init__(self):
        self.request = RequestsWithRetry(retrying=retrying_factory())

    def configure_retry(self, **kwargs):
        """Configure the retrying logic by passing keyword arguments destined for the `retrying.Retrying` class"""
        self.request = RequestsWithRetry(retrying=retrying_factory(**kwargs))
        return self

    def clover(self) -> CloverAPI:
        return CloverAPI(request=self.request)
