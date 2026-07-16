from __future__ import annotations

import logging
from typing import Any

from bookops_marc import Bib
from pymarc import Field, Indicators, Subfield

logger = logging.getLogger(__name__)


class StubMinimalFromPlatform:
    def __init__(self, var_fields: list[dict[str, Any]]) -> None:
        self.var_fields = var_fields

    def update_var_fields(
        self,
        copy_number: int,
        total: int,
        call_number: str,
        barcode: str,
        subject: str,
        shelf_number: str | None,
    ) -> None:
        self.var_fields.append(
            {
                "marcTag": "091",
                "ind1": " ",
                "ind2": " ",
                "subfields": [
                    {"tag": "a", "content": f"MLNYC {subject}"},
                    {"tag": "c", "content": shelf_number},
                ],
            }
        )
        self.var_fields.append(
            {
                "marcTag": "901",
                "ind1": " ",
                "ind2": " ",
                "subfields": [
                    {"tag": "n", "content": barcode},
                    {"tag": "o", "content": call_number},
                ],
            }
        )
        for field in self.var_fields:
            if field["marcTag"] == "245":
                field["subfields"].append(
                    {"tag": "p", "content": f"Copy {copy_number} of {total}"}
                )

    def create_marc_from_platform(self) -> Bib:
        record_type = "a"
        for field in self.var_fields:
            if field["marcTag"] is None:
                record_type = field["content"][6]
        bib = Bib()
        bib.library = "nypl"
        bib.leader = f"00000n{record_type}c a2200000 a 4500"
        for field in self.var_fields:
            if field.get("content") and field.get("marcTag"):
                bib.add_ordered_field(
                    Field(tag=field["marcTag"], data=field["content"])
                )
            elif field.get("marcTag") == "246":
                continue
            elif field.get("marcTag") and not field.get("content"):
                bib.add_ordered_field(
                    Field(
                        tag=field["marcTag"],
                        indicators=Indicators(field["ind1"], field["ind2"]),
                        subfields=[
                            Subfield(code=i["tag"], value=i["content"])
                            for i in field["subfields"]
                        ],
                    )
                )
        return bib
