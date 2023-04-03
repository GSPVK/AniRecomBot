from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        """
        The name of the file where the bot token will be read from (relative to the current directory)
        and its encoding.
        """
        env_file = '../.env'
        env_file_encoding = 'utf-8'


config = Settings()
