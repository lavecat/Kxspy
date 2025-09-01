import aiohttp
import logging

_LOG = logging.getLogger("kxspy.rest")

class RestApi:
    """
    The class for the REST API of kxspy.

    Parameters
    ---------
    kxs_network_rest_url: :class:`str`
        Rest url of the kxs network REST API.
    adminKey: :class:`str`
        Only for admin routs .
    """
    def __init__(self, kxs_network_rest_url: str = "https://network.kxs.rip", adminKey: str = None) -> None:
        self.rest_uri = kxs_network_rest_url
        self.admin_key = adminKey

    async def request(self, method: str, rout: str, data: dict = {}) -> dict or str:
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
            async with session.request(method, self.rest_uri + rout,json=data) as _response:
                _LOG.debug(f"{method} {self.rest_uri + rout}")
                if _response.content_type == "text/plain":
                    return await _response.text()

                response = await _response.json()

                _LOG.debug(response)

                if _response.status != 200:
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

    async def ig_count(self, gameId: str) -> dict:
        """
        This function makes a request to the kxs network REST API.

        Parameters
        ---------
        gameId: :class:`str`
            The game id.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", f"/ig-count/{gameId}")
        return res

    async def getLatestVersion(self) -> str:
        """
        This function makes a request to the kxs network REST API.

        Returns
        -------
        :class:`str`
            The response from the request.
        """
        res = await self.request("GET", "/getLatestVersion")
        return res

    async def on_join(self, gameid: int, exchangeKey: str) -> dict:
        """
        This function makes a request to the kxs network REST API.

        Returns
        -------
        :class:`str`
            The response from the request.
        """
        res = await self.request("GET", f"/exchange/joined/{gameid}/{exchangeKey}")
        return res

    async def user_manager_status(self) -> dict:
        """
        This function makes a request to the kxs network REST API ( kxs admin endpoint ).

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", "/users-manager/status",data={"adminKey":self.admin_key})
        return res

    async def broadcast(self, msg: str) -> dict:
        """
        This function makes a request to the kxs network REST API ( kxs admin endpoint ).

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", "/broadcast",data={"adminKey":self.admin_key,"msg":msg})
        return res

    async def blacklist(self, ip: str,reason: str) -> dict:
        """
        This function makes a request to the kxs network REST API ( kxs admin endpoint ).

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", "/users-manager/blacklist",data={"adminKey":self.admin_key,"ip":ip,"reason":reason})
        return res

    async def unblacklist(self, ip: str) -> dict:
        """
        This function makes a request to the kxs network REST API ( kxs admin endpoint ).

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", "/users-manager/unblacklist",data={"adminKey":self.admin_key,"ip":ip})
        return res