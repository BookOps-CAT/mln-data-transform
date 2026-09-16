from __future__ import annotations

import logging
import os
from typing import Any

from bookops_nypl_platform import PlatformSession, PlatformToken

logger = logging.getLogger(__name__)


class PlatformManager:
    def __init__(self) -> None:
        self.platform_token = PlatformToken(
            client_id=os.environ["NYPL_PLATFORM_CLIENT"],
            client_secret=os.environ["NYPL_PLATFORM_SECRET"],
            oauth_server=os.environ["NYPL_PLATFORM_OAUTH"],
        )

    def get_platform_bib(self, bib_id: str) -> dict[str, Any]:
        logger.debug(f"({bib_id}) Getting bib record from platform.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib(id=bib_id)
            return response.json()["data"]

    def get_platform_bib_items(self, bib_id: str) -> list[dict[str, Any]]:
        logger.debug(f"({bib_id}) Getting item records from platform.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib_items(id=bib_id)
            data = response.json()["data"]
            return data
