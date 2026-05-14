"""
Signed HTTP client for CrewAI agents.

Wraps requests with automatic Cloud Identity signing. Use this directly
in custom CrewAI tools that need to call other agents, or pass it to
tools that take an HTTP session.
"""

import os
import requests
from typing import Optional, Any
from citizenofthecloud import CloudIdentity


class CloudIdentityHTTPClient:
    """
    HTTP client that automatically signs requests with Cloud Identity headers.

    Usage:
        from citizenofthecloud_crewai import CloudIdentityHTTPClient

        client = CloudIdentityHTTPClient.from_env()
        response = client.get("https://other-agent.com/api/data")
    """

    def __init__(self, cloud_id: str, private_key: str):
        self.identity = CloudIdentity(cloud_id=cloud_id, private_key=private_key)
        self.session = requests.Session()

    @classmethod
    def from_env(
        cls,
        cloud_id_var: str = "CLOUD_ID",
        private_key_var: str = "CLOUD_PRIVATE_KEY",
    ) -> "CloudIdentityHTTPClient":
        cloud_id = os.environ.get(cloud_id_var)
        private_key = os.environ.get(private_key_var)
        if not cloud_id or not private_key:
            raise ValueError(
                f"Missing environment variables: {cloud_id_var} and/or {private_key_var}"
            )
        return cls(cloud_id=cloud_id, private_key=private_key)

    def _signed_headers(self, extra: Optional[dict] = None) -> dict:
        h = self.identity.sign()
        if extra:
            h.update(extra)
        return h

    def get(self, url: str, headers: Optional[dict] = None, **kw: Any) -> requests.Response:
        return self.session.get(url, headers=self._signed_headers(headers), **kw)

    def post(self, url: str, headers: Optional[dict] = None, **kw: Any) -> requests.Response:
        return self.session.post(url, headers=self._signed_headers(headers), **kw)

    def put(self, url: str, headers: Optional[dict] = None, **kw: Any) -> requests.Response:
        return self.session.put(url, headers=self._signed_headers(headers), **kw)

    def delete(self, url: str, headers: Optional[dict] = None, **kw: Any) -> requests.Response:
        return self.session.delete(url, headers=self._signed_headers(headers), **kw)

    def request(self, method: str, url: str, headers: Optional[dict] = None, **kw: Any) -> requests.Response:
        return self.session.request(method, url, headers=self._signed_headers(headers), **kw)
