from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware to throttle user actions to prevent spam and abuse by limiting
    the frequency of user interactions with the bot within a specified time interval.

    Attributes:
        caches (Dict[str, TTLCache]): A dictionary of TTLCache instances for managing
            rate limits with different keys, each cache can have its own TTL setting.
    """

    # Initialize caches with different throttling configurations
    caches = {
        "default": TTLCache(maxsize=10_000, ttl=2),
    }

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Middleware to throttle user actions to prevent spam and abuse by limiting
        the frequency of user interactions with the bot within a specified time interval.

        Example:
            Below is an example of using ThrottlingMiddleware with a message handler in an
            aiogram bot. The middleware is applied globally and the `@flags.rate_limit` decorator
            specifies a rate limit for the `/start` command handler.

            Setup:
            ```python
            from aiogram import Dispatcher

            dp = Dispatcher(bot)
            dp.message.middleware(ThrottlingMiddleware())
            ```

            Usage:
            ```python
            from aiogram import types
            from aiogram.dispatcher.filters.builtin import CommandStart
            from aiogram.dispatcher.flags import rate_limit

            @dp.message_handler(commands=['start'])
            @rate_limit(key="default", rate=5)  # Apply rate limit of 5 seconds
            async def handle_start(message: types.Message):
                await message.reply("Welcome to the bot! You can send this command every 5 seconds.")
            ```

            In this example, the `handle_start` function is decorated with `@rate_limit`,
            which uses the 'default' key from the ThrottlingMiddleware's caches. This setup
            ensures that users can only execute the `/start` command once every 5 seconds,
            effectively throttling frequent requests and preventing spam.
        """

        # Retrieve the throttling key from the data flags; use a default if not provided
        throttling_key = get_flag(data, "rate_limit")
        if throttling_key is not None:
            cache_key = throttling_key.get(
                "key", "default"
            )  # Default to 'default' if no key is specified
            cache = self.caches.get(
                cache_key, self.caches["default"]
            )  # Get the specific cache or default

            # Check if the user's ID is already in the cache (i.e., has recently made a request)
            if event.chat.id in cache:
                return  # Stop processing and throttle the user if their ID is found in the cache

            # Otherwise, add the user's ID to the cache to mark the start of their throttling period
            cache[event.chat.id] = (
                True  # Mark as True to indicate presence in the cache
            )

        # If not throttled, continue processing by calling the next handler
        return await handler(event, data)
