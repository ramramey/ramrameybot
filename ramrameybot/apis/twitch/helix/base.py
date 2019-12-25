import aiohttp
from urllib.parse import urlencode

from typing import Optional, List, Tuple


class ApiBase:
    url: str = "https://api.twitch.tv/helix/"

    # Authorizations
    authorization: Optional[str] = None
    client_id: Optional[str] = None

    # Query string parameters
    parameters = {""}
    scopes = {""}

    def __init__(self,
                 authorization: Optional[str] = None,
                 client_id: Optional[str] = None):

        self.authorization = authorization
        self.client_id = client_id

    @property
    def headers(self) -> dict:
        """Make request header"""
        headers: dict = {}

        if self.authorization:
            headers["Authorization"] = "Bearer " + self.authorization

        if self.client_id:
            headers["Client-ID"] = self.client_id

        return headers

    async def perform_get(self, parameters):
        """Perform HTTP GET with headers"""
        async with aiohttp.ClientSession(headers=self.headers) as sess:
            async with sess.get(self.url + "?" + urlencode(parameters)) as resp:
                return await resp.json()

    # TODO: Make function perform_put
