import dataclasses
from typing import Callable, Dict, Optional

import requests
from retrying import Retrying


class AuthError(RuntimeError):
    """A class to wrap when API Auth doesn't work"""


class BadInputError(RuntimeError):
    """A class to wrap when API is given bad input"""


def retrying_factory(**kwargs) -> Retrying:
    def _dont_retry_error_filter(e):
        """Return True if we should retry"""
        return not isinstance(e, (AuthError, BadInputError, FileNotFoundError))

    if "wait_exponential_multiplier" not in kwargs:
        kwargs["wait_exponential_multiplier"] = 250
    if "wait_exponential_max" not in kwargs:
        kwargs["wait_exponential_max"] = 10000
    if "stop_max_attempt_number" not in kwargs:
        kwargs["stop_max_attempt_number"] = 6
    if "retry_on_exception" not in kwargs:
        kwargs["retry_on_exception"] = _dont_retry_error_filter

    return Retrying(**kwargs)


@dataclasses.dataclass(frozen=True)
class RequestsWithRetry:
    retrying: Retrying
    headers: Optional[Dict] = None

    def get(self, url: str, callback: Optional[Callable] = None, **kwargs):
        return self.retrying.call(self._get_impl, url=url, callback=callback, **kwargs)

    def put(self, url: str, callback: Optional[Callable] = None, **kwargs):
        return self.retrying.call(self._put_impl, url=url, callback=callback, **kwargs)

    def post(self, url: str, callback: Optional[Callable] = None, **kwargs):
        return self.retrying.call(self._post_impl, url=url, callback=callback, **kwargs)

    @classmethod
    def _noop_callback(cls, response: requests.Response):
        """A callback that does nothing to the response object"""

    @classmethod
    def _handle_response(
        cls, response: requests.Response, callback: Optional[Callable] = None
    ):
        if not response.ok:
            url = response.request.url
            body = response.request.body
            txt = f"\nurl = {url}\nbody = {body}\nreason = {response.text}"
            if response.status_code == 400:
                raise BadInputError(f"Bad input to API:{txt}")
            if response.status_code in [401, 403]:
                raise AuthError(f"You are not authorised to access API:{txt}")
            if response.status_code == 404:
                raise FileNotFoundError(f"No resources found:{txt}")
            raise ValueError(
                f"API request was not ok -- status code {response.status_code}.{txt}"
            )

        # no-op callback
        if callback is None:
            callback = cls._noop_callback

        return callback(response)

    def _update_kwargs(self, kwargs: Dict):
        if "timeout" not in kwargs:
            kwargs["timeout"] = (2, 8)
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers

    def _get_impl(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self._update_kwargs(kwargs)
        with requests.get(url=url, **kwargs) as r:
            return self._handle_response(r, callback)

    def _put_impl(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self._update_kwargs(kwargs)
        with requests.put(url=url, **kwargs) as r:
            return self._handle_response(r, callback)

    def _post_impl(self, url: str, callback: Optional[Callable] = None, **kwargs):
        self._update_kwargs(kwargs)
        with requests.post(url=url, **kwargs) as r:
            return self._handle_response(r, callback)
