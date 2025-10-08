import logging
from .ws import WS
from .utils import get_random_username

_LOG = logging.getLogger("kxspy.client")

class Client:
    """
    The main class.
    """
    def __init__(
        self,
        ws_url: str = "wss://network.kxs.rip/",
        username: str = get_random_username(),
        enablevoicechat: bool = False,
        exchangekey: str = None
    ) -> None:
        self.ws = WS(
            ws_url=ws_url,
            username=username,
            enablevoicechat=enablevoicechat,
            exchangekey=exchangekey,
        )

    async def connect(self):
        """Connect to Kxs Network."""
        await self.ws._connect()
