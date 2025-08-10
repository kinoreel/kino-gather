import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SERVER: str
    DB_PORT: str
    OMDB_API_KEY: str
    TMDB_API_KEY: str
    AWS_API_KEY: str
    YOUTUBE_API_KEY: str

    @classmethod
    def from_env(cls, dotenv_path: str = Path(__file__).parent.parent / ".env"):
        load_dotenv(dotenv_path=dotenv_path)
        return cls(
            DB_DATABASE=os.getenv("DB_DATABASE", ""),
            DB_USER=os.getenv("DB_USER", ""),
            DB_PASSWORD=os.getenv("DB_PASSWORD", ""),
            DB_SERVER=os.getenv("DB_SERVER", ""),
            DB_PORT=os.getenv("DB_PORT", ""),
            OMDB_API_KEY=os.getenv("OMDB_API_KEY", ""),
            TMDB_API_KEY=os.getenv("TMDB_API_KEY", ""),
            AWS_API_KEY=os.getenv("AWS_API_KEY", ""),
            YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY", ""),
        )
