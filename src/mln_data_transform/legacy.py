from typing import Any


class LegacyTeacherSetData:
    """Useful data from a legacy bib record for a MyLibraryNYC Teacher Set."""

    def __init__(
        self,
        bib_id: str,
        item_ids: list[str],
        set_title: str,
        language: str,
        fixed_fields: list[dict[str, Any]],
        var_fields: list[dict[str, Any]],
    ) -> None:
        self.bib_id = bib_id
        self.item_ids = item_ids
        self.set_title = set_title
        self.fixed_fields = fixed_fields
        self.var_fields = var_fields
        self.language = language

    @property
    def call_number(self) -> str | None:
        field_091 = [i for i in self.var_fields if i["marcTag"] == "091"]
        if field_091:
            subfields_300 = field_091[0]["subfields"]
            return " ".join([i["content"] for i in subfields_300])
        return None

    @property
    def leader(self) -> str | None:
        leader = [i["content"] for i in self.var_fields if not i["marcTag"]]
        if leader:
            return leader[0]
        return None

    @property
    def isbns(self) -> list[str] | None:
        isbns = [i for i in self.var_fields if i["marcTag"] == "944"]
        if isbns:
            subfields_944 = isbns[0]["subfields"]
            isbn_string = " ".join([i["content"] for i in subfields_944])
            return isbn_string.split()
        return None

    @property
    def physical_description(self) -> str | None:
        field_300 = [i for i in self.var_fields if i["marcTag"] == "300"]
        if field_300:
            subfields_300 = field_300[0]["subfields"]
            return " ".join([i["content"] for i in subfields_300])
        return None

    @property
    def subjects(self) -> list[dict[str, Any]]:
        fields = [
            i
            for i in self.var_fields
            if isinstance(i["marcTag"], str) and i["marcTag"].startswith("6")
        ]
        return [
            {k: v for k, v in i.items() if k not in ["content", "fieldTag"]}
            for i in fields
        ]
