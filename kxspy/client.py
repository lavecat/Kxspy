import logging
import typing as t
from .ws import WS
from .events import Event
from .utils import get_random_username
from .rest import RestApi

_LOG = logging.getLogger("kxspy.client")

class Client:
    """
    The main class.
    """
    def __init__(
        self,
        ws_url: str = "wss://network.kxs.rip/",
        rest_url: str = "https://network.kxs.rip",
        username: str = get_random_username(),
        enablevoicechat: bool = False,
        exchangekey: str = None,
        admin_key: str = None
    ) -> None:
        self.ws = WS(
            ws_url=ws_url,
            username=username,
            enablevoicechat=enablevoicechat,
            exchangekey=exchangekey,
        )
        self.username = username
        self.rest = RestApi(rest_url,admin_key)

    def listen(self, event: t.Union[str, Event]):
        """
        Decorator shortcut for self.ws.emitter.on(event)
        Example:
            @client.on("ChatMessage")
            async def on_chat(evt): ...
        """
        return self.ws.emitter.on(event)

    async def connect(self):
        """Connect to Kxs Network."""
        await self.ws._connect()

    async def join_game(self, gameId):
        """Join a game by its ID."""
        await self.ws.send({"op": 3, "d": {"gameId": gameId,"user": self.username}})

    async def leave_game(self):
        """Leave the current game."""
        await self.ws.send({"op": 4, "d": {}})
