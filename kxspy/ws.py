import asyncio
import aiohttp
import logging
import typing as t

_LOG = logging.getLogger("Kxspy.ws")

class WS:
    def __init__(
            self,
            ws_url: str = "wss://network.kxs.rip/",
            loop: t.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.ws = None
        self.ws_url = ws_url
        self._loop = loop
        self.is_connect: bool = False
        self.is_authenticate: bool = False


    async def _connect(self):
        async with aiohttp.ClientSession(loop=self._loop) as session:
            self.session = session
            _LOG.info(f"Connecting to websocket {self.ws_url}")
            try:
                self.ws = await self.session.ws_connect(self.ws_url)
            except (aiohttp.ClientConnectorError, aiohttp.WSServerHandshakeError,
                    aiohttp.ServerDisconnectedError) as error:
                if isinstance(error, (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError)):
                    _LOG.error(f"Could not connect to websocket: {error}")
                    _LOG.warning("Reconnecting to websocket after 12 seconds")
                    await asyncio.sleep(12)
                    await self._connect()
                    return
                else:
                    _LOG.error(f"Exception WS: {error}")
            self.is_connect = True

            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self._loop.create_task(self.callback(msg.json()))
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    _LOG.error("Websocket closed")
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOG.error(msg.data)
                    break

            self.is_connect = False
            await self._connect()

    async def check_connection(self):
        while self.ws.closed is None or not self.ws.closed or not self.is_connected:
            _LOG.warning("Websocket closed unexpectedly - reconnecting in 12 seconds")
            await asyncio.sleep(12)
            await self._connect()

    async def callback(self, payload: dict):
        if payload["op"] == 1:
            _LOG.info("test huh")


    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):
        """
        Send msg to websocket
        """
        if not self.is_connected:
            _LOG.error("Not connected to websocket")
            return
        try:
            await self.ws.send_json(payload)
        except ConnectionResetError:
            _LOG.error("ConnectionResetError: Cannot write to closing transport")
            await self.check_connection()
            return