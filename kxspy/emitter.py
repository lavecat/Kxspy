import asyncio
import typing as t
from collections import deque
import logging
from .events import Event

_LOG = logging.getLogger("kxspy.emitter")

# |----------------------------------------------------------------------------|
# | https://github.com/HazemMeqdad/lavaplay.py/blob/master/lavaplay/emitter.py |
# |----------------------------------------------------------------------------|

class Emitter:
    """
    The class is a manger event from websocket.
    """

    def __init__(self) -> None:
        self._loop = asyncio.get_event_loop()
        self.listeners = deque()

    def add_listener(self, event: t.Union[str, Event], func: t.Callable):
        """
        Add listener for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        _LOG.debug(f"add listener {event}")
        event = event if isinstance(event, str) else event.__name__
        self.listeners.append({"event": event, "func": func})

    def remove_listener(self, event: t.Union[str, Event], func: t.Callable):
        """
        Remove listener for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        _LOG.debug(f"remove listener {event}")
        event = event if isinstance(event, str) else event.__name__
        self.listeners.remove([i for i in self.listeners if i["event"] == event and i["func"] == func])

    def emit(self, event: t.Union[str, t.Any], data: t.Any):
        """
        Emit for event dont use this.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        data: :class:`function`
            the data is revers to function callback
        """
        event_name = event if isinstance(event, str) else event.__name__
        events = [i for i in self.listeners if i["event"] == event_name]
        for event in events:
            _LOG.debug(f"dispatch {event} for {len(events)} listeners")
            if asyncio.iscoroutinefunction(event["func"]):
                self._loop.create_task(event["func"](data))
            else:
                _LOG.error("Events only async function")

    def on(self, event: t.Union[str, Event]):
        """
        Decorator to register async event handler.

        Example:
            @emitter.on("ChatMessage")
            async def handler(data): ...
        """
        event_name = event if isinstance(event, str) else event.__name__

        def decorator(func: t.Callable):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError(f"Handler for event '{event_name}' must be async")
            self.add_listener(event_name, func)
            return func

        return decorator