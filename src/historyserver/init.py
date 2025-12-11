from typing import Literal, cast
from .modules.logger.logger import Logger
from os import getenv
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")
log = Logger("log.log")
mode = cast(Literal["DEV", "PROD"], getenv("MODE"))