import kxspy
import asyncio
import aiohttp
import logging
from .events import *
from .emitter import Emitter
from .utils import get_random_username

_LOG = logging.getLogger("kxspy.ws")

class WS:
    def __init__(
            self,
            ws_url: str = "wss://network.kxs.rip/",
            username: str = get_random_username(),
            enablevoicechat: bool = False,
            exchangekey: str = None
    ) -> None:
        self.ws = None
        self.ws_url = ws_url
        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession()
        self.emitter = Emitter()
        self.is_connect: bool = False
        self.is_authenticate: bool = False
        self.username = username
        self.version = f"kxspy/{kxspy.__version__}"
        self.exchangeKey = exchangekey
        self.enableVoiceChat = enablevoicechat

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
            self.emitter.emit("HeartBeatEvent", HeartBeatEvent.from_kwargs(**payload["d"]))
            print(payload["d"])
        elif payload["op"] == 2: # IDENTIFY
            _LOG.info("test huh 2")
            _LOG.info(payload)
            self.emitter.emit("IdentifyEvent", IdentifyEvent.from_kwargs(**payload["d"]))
        elif payload["op"] == 3: # GAME START
            _LOG.info("test huh 3")
            if d.get("system") is not None:
                self.emitter.emit("ConfirmGameStart", ConfirmGameStart.from_kwargs(**payload["d"]))
            else:
                self.emitter.emit("GameStart", GameStart.from_kwargs(**payload["d"]))
            print(payload["d"])
        elif payload["op"] == 4: # GAME END
            _LOG.info("test huh 4")
            print(payload["d"])
        elif payload["op"] == 5: # KILL EVENT
            print(payload["d"])
            _LOG.info("test huh 5")
        elif payload["op"] == 6: # VERSION UPDATE
            print(payload["d"])
            _LOG.info("test huh 6")
        elif payload["op"] == 7: # CHAT MESSAGE
            print(payload["d"])
            _LOG.info("test huh 7")
        elif payload["op"] == 10: # HELLO (heartbeat interval)
            print(f"10: %s",payload)
            interval = d.get("heartbeat_interval", 3000)
            await self.send({"op": 2, "d": {"username": self.username, "isVoiceChat": self.enableVoiceChat,"v":self.version, "exchangeKey":self.exchangeKey}})
            await self.heartbeat(interval)
            self.emitter.emit("HelloEvent", HelloEvent.from_kwargs(**payload["d"]))
            _LOG.info("test huh 10")
        elif payload["op"] == 12: # EXCHANGE JOIN
            _LOG.info("test huh 12")
            self.emitter.emit("ExchangejoinEvent", ExchangejoinEvent.from_kwargs(**payload["d"]))
            print(payload)
        elif payload["op"] == 87: # BROADCAST MESSAGE
            print(payload["d"])
            self.emitter.emit("BroadCasteEvent", BroadCasteEvent.from_kwargs(**payload["d"]))
            _LOG.info("test huh 87 ( bro 1-10 BUT WHY 87 nah :p )")
        elif payload["op"] == 98: # VOICE CHAT UPDATE
            print(payload["d"])
            _LOG.info("test huh 98 ( bro 1-10 BUT WHY 98 nah :p )")
        elif payload["op"] == 99: # VOICE DATA
            print(payload["d"])
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

    async def join_game(self, gameId):
        await self.send({"op": 3, "d": {"gameId": gameId,"user": self.username}})