import logging
import os
from typing import Any

from bookops_nypl_platform import PlatformSession, PlatformToken
from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Record

from mln_data_transform.worldcat import FullWorldCatResponse

logger = logging.getLogger(__name__)


class BriefBibResponse:
    def __init__(self, wc_response: dict[str, Any]) -> None:
        self.cat_level: str | None = wc_response.get("catalogingInfo", {}).get(
            "levelOfCataloging"
        )
        self.oclc_number = wc_response["oclcNumber"]

    def sort_key(self) -> tuple[int, int]:
        if self.cat_level == " ":
            return (0, 0)
        if self.cat_level is None:
            return (2, 0)
        return (1, int(self.cat_level))


class Tranformer:
    def __init__(self) -> None:
        self.platform_token = PlatformToken(
            client_id=os.environ["NYPL_PLATFORM_CLIENT"],
            client_secret=os.environ["NYPL_PLATFORM_SECRET"],
            oauth_server=os.environ["NYPL_PLATFORM_OAUTH"],
        )
        self.worldcat_token = WorldcatAccessToken(
            key=os.environ["WORLDCAT_KEY"],
            secret=os.environ["WORLDCAT_SECRET"],
            scopes="WorldCatMetadataAPI",
        )

    def get_platform_bib(self, bib_id: str) -> dict[str, Any]:
        logger.info(f"Getting bib from platform for {bib_id}.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib(id=bib_id)
            return response.json()["data"]

    def get_platform_bib_items(self, bib_id: str) -> list[dict[str, Any]]:
        logger.info(f"Getting items from platform for {bib_id}.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib_items(id=bib_id)
            return response.json()["data"]

    def get_oclc_number_from_isbn(self, isbn: str, session: MetadataSession) -> str:
        logger.info(f"Getting worldcat brief bib record for {isbn}.")
        brief_bib_response = session.brief_bibs_search(
            q=f"bn:{isbn}", itemType="book", itemSubType="book-printbook"
        )
        parsed_responses = [
            BriefBibResponse(i) for i in brief_bib_response.json()["briefRecords"]
        ]
        sorted_recs = sorted(parsed_responses, key=BriefBibResponse.sort_key)
        return sorted_recs[0].oclc_number

    def get_full_record(self, oclc_number: str, session: MetadataSession) -> Record:
        logger.info(f"Getting worldcat full MARC record for {oclc_number}.")
        full_bib_response = session.bib_get(
            oclcNumber=oclc_number, responseFormat="application/marc"
        )
        return Record(data=full_bib_response.content)  # type: ignore

    def get_worldcat_data_for_parts(
        self, isbns: list[str]
    ) -> list[FullWorldCatResponse]:
        parts: list[FullWorldCatResponse] = []
        with MetadataSession(
            authorization=self.worldcat_token, timeout=(10, 10)
        ) as session:
            for isbn in isbns:
                logger.info(f"Searching worldcat for {isbn}.")
                oclc_number = self.get_oclc_number_from_isbn(isbn=isbn, session=session)
                full_rec = self.get_full_record(
                    oclc_number=oclc_number, session=session
                )
                full_resp = FullWorldCatResponse(isbn=isbn, wc_response=full_rec)
                parts.append(full_resp)
        return parts
