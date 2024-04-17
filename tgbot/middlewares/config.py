from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for aiogram bots to inject configuration into the data dictionary
    passed to message handlers.

    This middleware takes a `config` data class during initialization and inserts it
    into each event's data dictionary under the key 'config', allowing handlers
    to access configuration settings easily.

    Parameters:
        config (Config): A config data class containing configuration settings for the bot.

    Usage:
        Add this middleware to the dispatcher of an aiogram bot to make `config`
        accessible in every handler.
    """

    def __init__(self, config) -> None:
        """
        Initializes the middleware with a configuration dictionary.

        Args:
            config (Config): A configuration data class to be injected into message handlers.
        """
        self.config = config

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)
