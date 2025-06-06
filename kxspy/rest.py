import aiohttp
import logging
import typing as t

_LOG = logging.getLogger("kxspy.rest")


class RestApi:
    """
    The class for the REST API of kxspy.

    Parameters
    ---------
    kxs_network_rest__url: :class:`str`
        Rest url of the kxs network REST API.
    """
    def __init__(self, kxs_network_rest__url: str = "https://network.kxs.rip") -> None:
        self.rest_uri = kxs_network_rest__url
        self.headers = {
            "Authorization": password
        }

    async def request(self, method: str, rout: str, data: dict = {}) -> dict or None:
        """
        This function makes a request to the kxs network REST API.

        Parameters
        ---------
        method: :class:`str`
            method for request like `GET` or `POST` etc.
        rout: :class:`str`
            The route for request.
        data: :class:`dict`
            The data for request.

        Returns
        -------
        :class:`dict` or :class:`str`
            The response from the request.
        """
        rout = rout
        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.rest_uri + rout, headers=self.headers, json=data) as _response:
                _LOG.debug(f"{method} {self.rest_uri + rout}")
                if _response.headers["Content-Type"] == "application/json":
                    response = await _response.json()
                elif _response.headers["Content-Type"] == "text/plain":
                    response = await _response.text()

                _LOG.debug(response)

                if _response.status != 200 or 204:
                    _LOG.error(f"Request failed: {response}")
                return response


    async def online_count(self) -> dict:
        """
        This function makes a request to the kxs network REST API.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """

        res = await self.request("GET", "/online-count")
        return res
