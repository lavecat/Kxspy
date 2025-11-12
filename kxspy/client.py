import logging
import typing as t
import numpy as np
import aiohttp
from .ws import WS
from .events import Event
from .utils import get_random_username
from typing import Union, List, Optional
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
        isMobile: bool = False,
        isSecure: bool = True,
        admin_key: str = None,
        connect: bool = True,
        session: t.Optional[aiohttp.ClientSession] = None
    ) -> None:
        self.ws = WS(
            ws_url=ws_url,
            username=username,
            enable_voice_chat=enablevoicechat,
            exchange_key=exchangekey,
            connect=connect,
            isMobile=isMobile,
            isSecure=isSecure,
            session=session
        )
        self.username = username
        self.rest = RestApi(rest_url,admin_key,session)
        self.emitter = self.ws.emitter
        self._registered_listeners: t.List[t.Tuple[t.Any, t.Callable, t.Type[Event]]] = []


    def add_event_hooks(self, obj):
        """
        Scans the provided class ``obj`` for functions decorated with :func:`listener`,
        and sets them up to process Lavalink events.
        """
        for attr_name in dir(obj):
            method = getattr(obj, attr_name)
            events = getattr(method, "_kxspy_events", None)
            if not events:
                continue

            if not events:
                self.emitter.add_listener(event=None, func=method)
            else:
                for ev in events:
                    self.emitter.add_listener(event=ev, func=method)

    def remove_event_hooks(self, obj: t.Any):
        """
        Removes all previously registered listeners for an object.
        """
        to_remove = [r for r in self._registered_listeners if r[0] == obj]
        for _, method, ev in to_remove:
            try:
                self.emitter.remove_listener(event=ev, func=method)
                _LOG.debug(f"Removed listener: {method.__name__} for {ev}")
            except Exception as e:
                _LOG.warning(f"Failed to remove listener {method.__name__}: {e}")

            self._registered_listeners.remove((_, method, ev))

    async def connect(self):
        """Connect to Kxs Network."""
        await self.ws.connect()

    async def close(self):
        """Close connection to Kxs Network."""
        await self.ws.close()

    async def join_game(self, gameId):
        """Join a game by its ID."""
        await self.ws.send({"op": 3, "d": {"gameId": gameId,"user": self.username}})

    async def leave_game(self):
        """Leave the current game."""
        await self.ws.send({"op": 4, "d": {}})

    async def report_kill(self,killer: str, killed: str):
        """Report a kill in the game"""
        await self.ws.send({"op": 5, "d": {"killer":killer,"killed":killed}})

    async def check_version(self):
        """Check for the latest version of Kxs"""
        await self.ws.send({"op": 6, "d": {}})

    async def send_message(self,text: str):
        """Send a message to the in-game chat"""
        await self.ws.send({"op": 7, "d": {"text":text}})

    async def update_voicechat(self,isVoiceChat: bool):
        """Update the voice chat status"""
        await self.ws.send({"op": 98, "d": {"isVoiceChat":isVoiceChat}})

    async def send_voicedata(self, audio_data: Union[bytes, bytearray,np.ndarray, List[int]], user_id: Optional[str] = None):
        """Update the voice chat status"""
        if isinstance(audio_data, (bytes, bytearray)):
            int16_array = np.frombuffer(audio_data, dtype=np.int16)
            data_to_send = int16_array.tolist()
        elif isinstance(audio_data, np.ndarray) and audio_data.dtype == np.int16:
            data_to_send = audio_data.tolist()
        elif isinstance(audio_data, list):
            data_to_send = audio_data
        else:
            raise TypeError(
                "audio_data must be bytes, bytearray, numpy.ndarray[int16], or list[int]"
            )
        await self.ws.send({"op": 99, "d": data_to_send, "u":user_id or self.ws.uuid})

    async def ws_latency(self):
        """Send the latency of websocket"""
        return await self.ws.measure_latency()

