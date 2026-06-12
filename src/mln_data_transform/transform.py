from __future__ import annotations

import logging
import os
from typing import Any

from bookops_nypl_platform import PlatformSession, PlatformToken
from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Field, Record
from requests import Response

logger = logging.getLogger(__name__)


class BriefBibResponse:
    def __init__(self, wc_response: dict[str, Any]) -> None:
        self.cat_level: str | None = wc_response.get("catalogingInfo", {}).get(
            "levelOfCataloging"
        )
        self.oclc_number = wc_response["oclcNumber"]

    def sort_key(self) -> tuple[int, int]:
        if self.cat_level in [" ", "I"]:
            return (0, 0)
        if self.cat_level is None:
            return (2, 0)
        if self.cat_level in ["K", "L", "M"]:
            return (1, 9)
        return (1, int(self.cat_level))


class FullWorldCatResponse:
    def __init__(self, isbn: str, wc_response: Record) -> None:
        self.isbn = isbn
        self.record = wc_response
        self.subject_fields: list[Field] = wc_response.subjects

    @property
    def author_data(self) -> Field | None:
        field = (
            self.record.get("100") or self.record.get("110") or self.record.get("111")
        )
        return field if field else None

    @property
    def author_name(self) -> str | None:
        if not self.author_data:
            return None
        return self.author_data["a"].rstrip(" ,")

    @property
    def author_dates(self) -> str | None:
        if not self.author_data:
            return None
        return self.author_data.get("d", "").rstrip(",")

    @property
    def description(self) -> str:
        try:
            return self.record["520"].format_field()
        except KeyError:
            return ""

    @property
    def title(self) -> str:
        return self.record["245"]["a"].strip(" :/")

    @property
    def pub_date(self) -> str | None:
        pub_date = self.record.pubyear
        if isinstance(pub_date, str):
            return pub_date.strip("[].")
        return pub_date

    @property
    def subjects(self) -> list[dict[str, Any]]:
        subject_list = []
        for subject in self.subject_fields:
            if subject.indicator2 not in ["0", "7"]:
                continue
            subject_subfields = [(i.code, i.value) for i in subject.subfields]
            if subject.indicator2 == "0" or (
                subject.indicator2 == "7" and ("2", "lcgft") in subject_subfields
            ):
                subject_list.append(
                    {
                        "tag": subject.tag,
                        "ind1": subject.indicator1,
                        "ind2": subject.indicator2,
                        "subfields": subject_subfields,
                    }
                )
        return subject_list


class PlatformManager:
    def __init__(self) -> None:
        self.platform_token = PlatformToken(
            client_id=os.environ["NYPL_PLATFORM_CLIENT"],
            client_secret=os.environ["NYPL_PLATFORM_SECRET"],
            oauth_server=os.environ["NYPL_PLATFORM_OAUTH"],
        )

    def get_platform_bib(self, bib_id: str) -> dict[str, Any]:
        logger.info(f"Getting bib record from platform for {bib_id}.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib(id=bib_id)
            return response.json()["data"]

    def get_platform_bib_items(self, bib_id: str) -> list[dict[str, Any]]:
        logger.info(f"Getting items from platform for {bib_id}.")
        with PlatformSession(authorization=self.platform_token) as session:
            response = session.get_bib_items(id=bib_id)
            data = response.json()["data"]
            logger.info(f"{len(data)} item records found for bib b{bib_id}a.")
            return data


class WorldcatManager:
    def __init__(self) -> None:
        self.worldcat_token = WorldcatAccessToken(
            key=os.environ["WORLDCAT_KEY"],
            secret=os.environ["WORLDCAT_SECRET"],
            scopes="WorldCatMetadataAPI",
        )

    def get_oclc_number_from_isbn(self, response: Response) -> str:
        parsed_responses = [
            BriefBibResponse(i) for i in response.json()["briefRecords"]
        ]
        sorted_recs = sorted(parsed_responses, key=BriefBibResponse.sort_key)
        return [i.oclc_number for i in sorted_recs][0]

    def get_full_record(self, oclc_number: str, session: MetadataSession) -> Record:
        full_bib_response = session.bib_get(
            oclcNumber=oclc_number, responseFormat="application/marc"
        )
        return Record(data=full_bib_response.content)  # type: ignore

    def get_worldcat_data_for_parts(
        self, isbns: list[str]
    ) -> list[FullWorldCatResponse]:
        parts: list[FullWorldCatResponse] = []
        logger.info(f"Record contains {len(isbns)} ISBN(s) to check.")
        with MetadataSession(
            authorization=self.worldcat_token, timeout=(10, 10)
        ) as session:
            for isbn in isbns:
                logger.info(f"ISBN {isbn}: retrieving brief bib record.")
                brief_bib = session.brief_bibs_search(
                    q=f"bn:{isbn}", itemType="book", itemSubType="book-printbook"
                )
                oclc_number = self.get_oclc_number_from_isbn(response=brief_bib)
                logger.info(
                    f"ISBN {isbn}: retrieving full bib record "
                    f"(OCLC number: {oclc_number})."
                )
                full_rec = self.get_full_record(
                    oclc_number=oclc_number, session=session
                )
                full_resp = FullWorldCatResponse(isbn=isbn, wc_response=full_rec)
                parts.append(full_resp)
        return parts
