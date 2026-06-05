import logging
from typing import Any

from pymarc import Field, Record

logger = logging.getLogger(__name__)


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
    def full_title(self) -> str:
        title_field = self.record["245"]
        title = title_field["a"]
        subtitle = title_field.get("b")
        if subtitle:
            title += f" {subtitle}"
        return title.strip(" /")

    @property
    def pub_date(self) -> str | None:
        pub_date = self.record.pubyear
        if isinstance(pub_date, str):
            return pub_date.strip("[].")
        return pub_date

    @property
    def statement_of_responsibility(self) -> str | None:
        statement_of_responsibility = self.record["245"].get("c")
        if isinstance(statement_of_responsibility, str):
            return statement_of_responsibility.strip(".")
        return statement_of_responsibility

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
