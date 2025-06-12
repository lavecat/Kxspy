import asyncio
import aiohttp
import logging
import kxspy

_LOG = logging.getLogger("Kxspy.ws")

class WS:
    def __init__(
            self,
            ws_url: str = "wss://network.kxs.rip/"
    ) -> None:
        self.ws = None
        self.ws_url = ws_url
        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession()
        self.is_connect: bool = False
        self.is_authenticate: bool = False
        self.version = f"kxspy/{kxspy.__version__}"

    def connect(self) -> asyncio.Task:
        """ Attempts to establish a connecion to Kxs Network. """
        return self._loop.create_task(self._connect())

    async def _connect(self):
        async with self._session as session:
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
        while self.ws.closed is not None or not self.ws.closed or not self.is_connected:
            _LOG.warning("Websocket closed unexpectedly - reconnecting in 12 seconds")
            await asyncio.sleep(12)
            await self._connect()

    async def heartbeat(self, interval):
        while self.ws is not None and not self.ws.closed and self.is_connected:
            try:
                await asyncio.sleep(interval / 3000)
                await self.send({"op": 1, "d": {}})
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOG.error(f"Heartbeat error: {e}")
                break


    async def callback(self, payload: dict):
        d = payload["d"]
        if payload["op"] == 1: # HEARTBEAT
            _LOG.info("test huh 1")
        elif payload["op"] == 2: # IDENTIFY
            _LOG.info("test huh 2")
        elif payload["op"] == 3: # GAME START
            _LOG.info("test huh 3")
        elif payload["op"] == 4: # GAME END
            _LOG.info("test huh 4")
        elif payload["op"] == 5: # KILL EVENT
            _LOG.info("test huh 5")
        elif payload["op"] == 6: # VERSION UPDATE
            _LOG.info("test huh 6")
        elif payload["op"] == 7: # CHAT MESSAGE
            _LOG.info("test huh 7")
        elif payload["op"] == 10: # HELLO (heartbeat interval)
            interval = d.get("heartbeat_interval", 3000)
            await self.send({"op": 2, "d": {"username": "Undevrdm:D", "isVoiceChat": False,"v":self.version}})  # Just for try
            await self.heartbeat(interval)
            _LOG.info("test huh 10")
        elif payload["op"] == 87: # BROADCAST MESSAGE
            _LOG.info("test huh 87 ( bro 1-10 BUT WHY 87 nah :p )")
        elif payload["op"] == 98: # VOICE CHAT UPDATE
            _LOG.info("test huh 98 ( bro 1-10 BUT WHY 98 nah :p )")
        elif payload["op"] == 99: # VOICE CHAT UPDATE
            _LOG.info("test huh 99 ( bro 1-10 BUT WHY 99 ( oh 98 - 99 yeah ) nah :p )")
        else:
            _LOG.error(f"Unknown webdocket Message: {payload} ")

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):
        """
        Send payload to the websocket.
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