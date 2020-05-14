import aiohttp
from urllib.parse import urlencode
from datetime import datetime

from typing import Optional, List, Tuple


class ApiBase:
    url: str = "https://api.twitch.tv/helix/"

    # Authorizations
    authorization: Optional[str] = None
    client_id: Optional[str] = None

    # Query string parameters
    parameters = {""}
    scopes = {""}
    auth_require = {"client_id", "authorization"}  # Now all API requires Access token

    last_response = None

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

        start = datetime.now()
        print(start.strftime("%Y-%m-%d %T"), "Performing Twitch API Helix: route " + self.url)
        async with aiohttp.ClientSession(headers=self.headers) as sess:
            async with sess.get(self.url + "?" + urlencode(parameters)) as resp:
                self.last_response = resp
                data = await resp.json()
                print(datetime.now().strftime("%Y-%m-%d %T"),
                      "Closing Twitch API Helix: route " + self.url + " (took {}ms)".format((datetime.now() - start).total_seconds() * 1000))
                return data

    # TODO: Make function perform_put
