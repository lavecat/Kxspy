import asyncio
import logging
import aiohttp
import kxspy
from .emitter import Emitter
from .utils import get_random_username
from .events import *

_LOG = logging.getLogger("kxspy.ws")

MESSAGE_QUEUE_MAX_SIZE = 25

class WS:
    """Handles the WebSocket connection to the Kxs network."""
    def __init__(
        self,
        ws_url: str = "wss://network.kxs.rip/",
        username: str | None = None,
        enable_voice_chat: bool = False,
        exchange_key: str | None = None,
        connect: bool = True,
    ):
        self.ws_url = ws_url
        self.username = username or get_random_username()
        self.enable_voice_chat = enable_voice_chat
        self.exchange_key = exchange_key

        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession()
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._message_queue: list[dict] = []
        self._listen_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._destroyed = False

        self.is_connect: bool = False
        self.is_authenticated: bool = False
        self.uuid = None

        self.emitter = Emitter()
        self.version = f"kxspy/{kxspy.__version__}"

        if connect:
            self.connect()

    def connect(self) -> asyncio.Task:
        if self._destroyed:
            raise IOError("Cannot connect: transport destroyed.")

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()

        return self._loop.create_task(self._connect())

    async def _connect(self):
        await self.close()

        attempt = 0
        while not self._destroyed and not self.is_connect:
            attempt += 1
            try:
                _LOG.info(f"Connecting to WebSocket: {self.ws_url}")
                self._ws = await self._session.ws_connect(self.ws_url, heartbeat=60)
                self.is_connect = True
                _LOG.info("WebSocket connection established.")
                self._listen_task = self._loop.create_task(self._listen())
                break
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                delay = min(10 * attempt, 60)
                _LOG.error(
                    f"Connection failed ({type(exc).__name__}: {exc}), retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            except (aiohttp.ClientConnectorError, aiohttp.WSServerHandshakeError,
                    aiohttp.ServerDisconnectedError) as error:
                if isinstance(error, (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError)):
                    delay = min(10 * attempt, 60)
                    _LOG.error(
                        f"Connection failed ({type(error).__name__}: {error}), retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    _LOG.error(f"Exception WS: {error}")

    async def close(self, code=aiohttp.WSCloseCode.OK):
        if self._listen_task:
            self._listen_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._ws:
            try:
                await self._ws.close(code=code)
            except Exception:
                pass
            finally:
                self._ws = None
                self.is_connect = False

    async def destroy(self):
        self._closing = True

        tasks = []
        for task in [self._listen_task, self._heartbeat_task]:
            if task and not task.done():
                task.cancel()
                tasks.append(task)

        if self._ws and not self._ws.closed:
            await self._ws.close()

        if self._session and not self._session.closed:
            await self._session.close()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._ws = None
        self.is_connect = False
        self._destroyed = True
        _LOG.info("Kxspy WS destroyed cleanly.")


    async def _listen(self):
        assert self._ws is not None
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    _LOG.debug(f"Received message: {msg.data}")
                    self._loop.create_task(self._handle_message_safe(msg))
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSED,
                ):
                    _LOG.warning("WebSocket closed by server.")
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOG.error(f"WebSocket error: {msg.data}")
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOG.exception(f"Unexpected error while listening websocket message: {e}")

        self.is_connect = False
        self._ws = None
        if not self._destroyed:
            _LOG.info("Reconnecting after disconnection...")
            self._loop.create_task(self._connect())

    async def _handle_message_safe(self, msg: aiohttp.WSMessage):
        try:
            await self._handle_message(msg.json())
        except Exception:
            _LOG.exception("Error while handling websocket message")

    async def _handle_message(self, payload: dict):
        op = payload.get("op")
        d = payload.get("d", {})

        if op == 1:  # Heartbeat
            self.emitter.emit("HeartBeatEvent", HeartBeatEvent.from_kwargs(**d))
        elif op == 2:  # Identify
            self.uuid = d.get("uuid")
            self.emitter.emit("IdentifyEvent", IdentifyEvent.from_kwargs(**d))
        elif op == 3:  # Game start
            event = GameStart.from_kwargs(**d) if d.get("system") else ConfirmGameStart.from_kwargs(**d)
            self.emitter.emit(event.__class__.__name__, event)
        elif op == 4:  # Game end
            event = GameEnd.from_kwargs(**d) if d.get("left") else ConfirmGameEnd.from_kwargs(**d)
            self.emitter.emit(event.__class__.__name__, event)
        elif op == 5: # KILL EVENT
            self.emitter.emit("KillEvent", KillEvent.from_kwargs(**d))
        elif op == 6: # VERSION UPDATE
            self.emitter.emit("VersionUpdate", VersionUpdate.from_kwargs(**d))
        elif op == 7: # CHAT MESSAGE
            self.emitter.emit("ChatMessage", ChatMessage.from_kwargs(**d))
        elif op == 10:  # Hello (heartbeat interval)
            interval = d.get("heartbeat_interval", 3000)
            await self.send({"op": 2,"d":{"username":self.username,"isVoiceChat":self.enable_voice_chat,"v":self.version,"exchangeKey":self.exchange_key}})
            await self._start_heartbeat(interval)
            self.emitter.emit("HelloEvent", HelloEvent.from_kwargs(**d))
        elif op == 12: # EXCHANGE KEY JOIN
            self.emitter.emit("ExchangejoinEvent", ExchangejoinEvent.from_kwargs(**d))
        elif op == 13: # EXCHANGE KEY ONLINE
            self.emitter.emit("ExchangeOnlineEvent", ExchangeOnlineEvent.from_kwargs(**d))
        elif op == 14: # EXCHANGE KEY OFFLINE
            self.emitter.emit("ExchangeOfflineEvent", ExchangeOfflineEvent.from_kwargs(**d))
        elif op == 15: # GAME ALIVE EXCHANGE KEY
            self.emitter.emit("ExchangeGameAliveEvent", ExchangeGameAliveEvent.from_kwargs(**d))
        elif op == 16: # GAME END EXCHANGE KEY
            print(payload)
            d["data"]["stuff"] = Stuff.from_kwargs(**d["data"]["stuff"])
            self.emitter.emit("ExchangeGameEnd", ExchangeGameEnd.from_kwargs(**d["data"]))
        elif op == 87: # BROADCAST MESSAGE
            self.emitter.emit("BroadCasteEvent", BroadCasteEvent.from_kwargs(**d))
            _LOG.info("Received BroadcastEvent (op 87).")
        elif op == 98: # VOICE CHAT UPDATE
            event = (
                VoiceChatUpdate.from_kwargs(**d)
                if d.get("user")
                else ConfirmVoiceChatUpdate.from_kwargs(**d)
            )
            self.emitter.emit(event.__class__.__name__, event)
        elif op == 99: # VOICE DATA
            self.emitter.emit("VoiceData", VoiceData(d=d, u=payload.get("u")))
        else:
            _LOG.warning(f"Unknown opcode: {op} — payload: {payload}")

    async def send(self, payload: dict):
        if not self.is_connect or not self._ws:
            if len(self._message_queue) >= MESSAGE_QUEUE_MAX_SIZE:
                _LOG.warning("Message queue full, discarding payload.")
                return
            _LOG.debug("Queueing payload until reconnected.")
            self._message_queue.append(payload)
            return

        try:
            await self._ws.send_json(payload)
        except ConnectionResetError:
            _LOG.warning("Connection reset during send, requeueing payload.")
            self._message_queue.append(payload)
            await self._connect()


    async def _start_heartbeat(self, interval: int):
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        self._heartbeat_task = self._loop.create_task(self._heartbeat(interval))

    async def _heartbeat(self, interval: int):
        while self.is_connect and self._ws and not self._ws.closed:
            try:
                await asyncio.sleep(interval / 3000)
                await self.send({"op": 1, "d": {}})
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOG.error(f"Heartbeat error: {e}")
                break

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self._ws.closed is False

    @property
    def uuid(self) -> bool:
        return self.uuid