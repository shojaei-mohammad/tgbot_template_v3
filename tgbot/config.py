import logging
from typing import Optional

from pydantic import BaseModel, SecretStr, ValidationError
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


class TgBot(BaseSettings, env_prefix="TGBOT_"):
    """
    Creates the TgBot object from environment variables.
    """

    token: SecretStr
    admin_ids: list[int]
    use_redis: bool = False


class DbConfig(BaseSettings, env_prefix="DB_"):
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: SecretStr
    user: str
    database: str
    port: int = 5432

    # For SQLAlchemy
    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this database configuration.
        """
        # TODO: If you're using SQLAlchemy, move the import to the top of the file!
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password.get_secret_value(),
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=True)


class RedisConfig(BaseSettings, env_prefix="REDIS_"):
    """
    Redis configuration class.

    Attributes
    ----------
    password : Optional(SecretStr)
        The password used to authenticate with Redis.
    port : Optional(int)
        The port where Redis server is listening.
    host : Optional(str)
        The host where Redis server is located.
    """

    password: Optional[SecretStr]
    port: Optional[int] = 6379
    host: Optional[str] = "localhsot"

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.password:
            return (
                f"redis://:{self.password.get_secret_value()}@{self.host}:{self.port}/0"
            )
        else:
            return f"redis://{self.host}:{self.port}/0"


class Miscellaneous(BaseSettings, env_prefix="MISC_"):
    """
    Miscellaneous configuration class.

    This class holds settings for various other parameters.
    It merely serves as a placeholder for settings that are not part of other categories.

    Attributes
    ----------
    other_params : str, optional
        A string used to hold other various parameters as required (default is None).
    """

    other_params: str = None


class Config(BaseModel):
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    misc : Miscellaneous
        Holds the values for miscellaneous settings.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    tg_bot: TgBot
    db: DbConfig
    redis: RedisConfig
    misc: Optional[Miscellaneous] = None


def load_config() -> Config:
    try:

        return Config(
            tg_bot=TgBot(),
            db=DbConfig(),
            redis=RedisConfig(),
        )
    except ValidationError as e:
        # Handle missing or invalid configurations
        logging.error("Failed to load configuration: %s", e)
        raise
