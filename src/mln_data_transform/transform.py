from __future__ import annotations

import logging
import os
from typing import Any

from bookops_nypl_platform import PlatformSession, PlatformToken
from bookops_worldcat import MetadataSession, WorldcatAccessToken
from pymarc import Field, Record

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
    def __init__(self, id: str, wc_response: Record) -> None:
        self.id = id
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
    def pub_date(self) -> str | None:
        pub_date = self.record.pubyear
        if isinstance(pub_date, str):
            return pub_date.strip("[].")
        return pub_date

    @property
    def title(self) -> str:
        return self.record["245"]["a"].strip(" :/.")

    @property
    def subjects(self) -> list[dict[str, Any]]:
        subject_list = []
        for subject in self.subject_fields:
            if subject.indicator2 not in ["0", "1", "7"]:
                continue
            subject_subfields = [(i.code, i.value) for i in subject.subfields]
            if subject.indicator2 in ["0", "1"] or (
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "author_name": self.author_name,
            "author_dates": self.author_dates,
            "description": self.description,
            "pub_date": self.pub_date,
            "subjects": self.subjects,
            "title": self.title,
        }


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


class WorldcatManager:
    def __init__(self) -> None:
        self.worldcat_token = WorldcatAccessToken(
            key=os.environ["WORLDCAT_KEY"],
            secret=os.environ["WORLDCAT_SECRET"],
            scopes="WorldCatMetadataAPI",
        )
        self.session = None

    def __enter__(self, *args, **kwargs) -> WorldcatManager:
        self.session = MetadataSession(
            authorization=self.worldcat_token, timeout=(10, 10), totalRetries=2
        )
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.session.close()

    def parse_brief_bib(
        self, brief_records: list[dict[str, Any]], sort: bool = True
    ) -> list[str]:
        parsed_responses = [BriefBibResponse(i) for i in brief_records]
        if sort:
            parsed_responses = sorted(parsed_responses, key=BriefBibResponse.sort_key)
        return [i.oclc_number for i in parsed_responses]

    def get_full_record(self, id: str, oclc_number: str) -> FullWorldCatResponse:
        logger.debug(
            f"ISBN/UPC {id}: retrieving full bib record (OCLC number: {oclc_number})."
        )
        full_bib_response = self.session.bib_get(
            oclcNumber=oclc_number, responseFormat="application/marc"
        )
        record = Record(data=full_bib_response.content)  # type: ignore
        return FullWorldCatResponse(id=id, wc_response=record)

    def get_oclc_number_from_id(self, id: str, format: str) -> list[dict[str, Any]]:
        query = f"sn:{id}"
        if format == "dvd":
            brief_bibs = self.dvd_brief_bib_search(query)
        elif format == "lprint":
            brief_bibs = self.large_print_brief_bib_search(query)
        else:
            brief_bibs = self.book_brief_bib_search(query)
        if brief_bibs:
            return brief_bibs
        raise ValueError(f"No records found in WorldCat for {id}.")

    def dvd_brief_bib_search(self, query: str) -> list[dict[str, Any]]:
        brief_bib = self.session.brief_bibs_search(q=query, itemSubType="video-dvd")
        brief_bib_json = brief_bib.json()
        brief_records = [
            i
            for i in brief_bib_json.get("briefRecords", [])
            if i and i["specificFormat"] == "DVD"
        ]
        return self.parse_brief_bib(brief_records=brief_records, sort=False)

    # def game_brief_bib_search(self, query: str) -> list[dict[str, Any]]:
    #     brief_bib = self.session.brief_bibs_search(q=query, itemType="game")
    #     brief_bib_json = brief_bib.json()
    #     brief_records = [
    #         i
    #         for i in brief_bib_json.get("briefRecords", [])
    #         if i and i["generalFormat"] == "Game"
    #     ]
    #     return self.parse_brief_bib(brief_records=brief_records, sort=False)

    def large_print_brief_bib_search(self, query: str) -> list[dict[str, Any]]:
        brief_bib = self.session.brief_bibs_search(
            q=query, itemSubType="book-largeprint"
        )
        brief_bib_json = brief_bib.json()
        brief_records = [
            i
            for i in brief_bib_json.get("briefRecords", [])
            if i and i["specificFormat"] == "LargePrint"
        ]
        return self.parse_brief_bib(brief_records=brief_records, sort=False)

    def book_brief_bib_search(self, query: str) -> list[dict[str, Any]]:
        brief_bib = self.session.brief_bibs_search(
            q=query, itemSubType="book-printbook"
        )
        brief_bib_json = brief_bib.json()
        brief_records = [
            i
            for i in brief_bib_json.get("briefRecords", [])
            if i and i["specificFormat"] == "PrintBook"
        ]
        return self.parse_brief_bib(brief_records=brief_records, sort=True)

    def get_worldcat_data_for_part(
        self, id: str, format: str | None = "book"
    ) -> dict[str, Any]:
        if not id:
            return {
                "title": f"{format.upper()} (missing identifier)",
                "description": "",
            }
        logger.debug(f"ISBN/UPC {id}: retrieving brief bib record.")
        oclc_numbers = self.get_oclc_number_from_id(id=id, format=format)
        first_rec = None
        for oclc in oclc_numbers:
            full_rec = self.get_full_record(oclc_number=oclc, id=id)
            if not full_rec.description:
                logger.debug(
                    f"ISBN/UPC {id}: full bib record for "
                    f"{oclc} missing description. Checking next record if present."
                )
                first_rec = full_rec
                continue
            else:
                return full_rec.to_dict()
        return first_rec.to_dict()
