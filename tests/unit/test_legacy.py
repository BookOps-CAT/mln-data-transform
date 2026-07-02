import copy

import pytest

from mln_data_transform.legacy import (
    LegacyBibData,
    LegacyItemData,
    LegacyTeacherSet,
    LegacyTeacherSetData,
)


class TestLegacyBibData:
    def test_legacy_bib_data(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == ["9781234567897", "9780987654328"]
        assert legacy_bib.physical_description == "10 item(s)"
        assert legacy_bib.record_type == "a"
        assert legacy_bib.copy_count == 2

    def test_legacy_bib_data_missing_fields(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields={},
            language=test_bib_data["lang"],
        )
        assert legacy_bib.physical_description is None
        assert legacy_bib.record_type == "a"

    def test_legacy_bib_data_missing_isbns(self, test_bib_data):
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields={},
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.isbns
        assert str(exc.value) == "(19538471) Record does not contain ISBNs."

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("Five copies of two titles", 5),
            ("Three copies of ten titles", 3),
            ("Five copies of six titles", 5),
            ("Three copies of eight titles", 3),
            ("Four copies of four titles", 4),
            ("Five copies of four titles", 5),
            ("Five copies of two titles", 5),
            ("2 copies of 11 titles", 2),
            ("1 copy of 16 titles", 1),
            ("2 copies of 13 titles", 2),
            ("3 copies of 11 titles", 3),
            ("One copy of 35 titles", 1),
            ("Tabletop Game - ", 1),
            ("Game - ", 1),
            ("DVD - ", 1),
            ("Game (Board Game) - ", 1),
            ("15 item(s) + 1 DVD.", 1),
            ("2 copies of 12 titles + 1 Playaway Audiobook.", 2),
            ("11 item(s) + 1 Playaway Audiobook", 1),
            ("Topic Set (24 books + 1 Playaway Audiobook)", 1),
        ],
    )
    def test_legacy_bib_data_pattern_matching(self, test_bib_data, arg, output):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "500",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": "Teacher set"}],
            },
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "520",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": f"{arg} Baz - Qux. "}],
            },
        ]
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.copy_count == output

    def test_legacy_bib_data_pattern_matching_no_valid_match(self, test_bib_data):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "500",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": "Teacher set"}],
            }
        ]
        with pytest.raises(ValueError) as exc:
            legacy_bib = LegacyBibData(
                bib_id=test_bib_data["id"],
                set_title=test_bib_data["title"],
                var_fields=test_bib_data["varFields"],
                language=test_bib_data["lang"],
            )
            legacy_bib.copy_count
        assert str(exc.value) == "Copy info pattern does not match for 19538471."

    @pytest.mark.parametrize(
        "arg,enhanced,grade,set_type,subject",
        [
            ("Math B Assorted 1", None, "B", "TOPIC", "MAT"),
            ("FRLA D Genre - Horror 1", None, "D", "TOPIC", "FRLA"),
            ("Language Arts CHI YA Book Club 185", None, "E", "CLUB", "CHLA"),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1",
                "E",
                "C",
                "CLUB",
                "SOC",
            ),
            ("Arts A BIOG - Musicians (Jazz) 1", None, "A", "TOPIC", "ART"),
            ("ELA D Horror Large Print 1", None, "D", "LPRINT", "ELA"),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29",
                None,
                "D",
                "CLUB",
                "ELA",
            ),
            ("Language Arts ENG YA Audiobook 194", None, "E", "AUDIO", "ELA"),
            ("Game C Catan 1", None, "C", "GAME", "GAME"),
            ("ELA D Storytelling 1", None, "D", "STORY", "ELA"),
            ("Language Arts SPA J 135", None, "C", "TOPIC", "SPLA"),
            ("Language Arts POL J 99", None, "C", "TOPIC", "WorldLang"),
            ("Social Studies ENG J Picture Book 155", None, "C", "TOPIC", "SOC"),
        ],
    )
    def test_legacy_bib_data_call_number_patterns(
        self, test_bib_data, arg, enhanced, grade, set_type, subject
    ):
        var_fields = [
            i for i in test_bib_data["varFields"] if i["marcTag"] not in ["091", "521"]
        ]
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "091",
                "fieldTag": "c",
                "subfields": [{"tag": "a", "content": f"Teacher Set {arg}"}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        assert legacy_bib.enhanced == enhanced
        assert legacy_bib.grade_level == grade
        assert legacy_bib.set_type == set_type
        assert legacy_bib.subject == subject

    @pytest.mark.parametrize(
        "grade,output",
        [
            ("1-12", "E"),
            ("0-3", "A"),
            ("1-3", "B"),
            ("K-3", "B"),
            ("0-5", "A"),
            ("Pre-K-3", "A"),
            ("9-12.", "E"),
            ("6-11", "D"),
        ],
    )
    def test_legacy_bib_data_grade_level(self, test_bib_data, grade, output):
        var_fields = [i for i in test_bib_data["varFields"] if i["marcTag"] != "521"]
        var_fields.append(
            {
                "ind1": "2",
                "ind2": " ",
                "content": None,
                "marcTag": "521",
                "fieldTag": "n",
                "subfields": [{"tag": "a", "content": grade}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        assert legacy_bib.grade_level == output

    def test_legacy_bib_data_call_number_pattern_error(self, test_bib_data):
        var_fields = [i for i in test_bib_data["varFields"] if i["marcTag"] != "091"]
        var_fields.append(
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "091",
                "fieldTag": "c",
                "subfields": [{"tag": "a", "content": "call number"}],
            }
        )
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=var_fields,
            language=test_bib_data["lang"],
        )
        with pytest.raises(ValueError) as exc:
            legacy_bib.call_number_components
        assert (
            str(exc.value)
            == "Call number 'call number' does not match pattern. Cannot extract components."
        )

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("9780789308849 ", ["9780789308849"]),
            ("978-0-78-930884-9 ", ["9780789308849"]),
            (" 0789308843", ["0789308843"]),
            ("0-7893-0884-3", ["0789308843"]),
            (" 068816241X ", ["068816241X"]),
            ("816069239", ["0816069239"]),
            ("766023931", ["0766023931"]),
            ("439364264", ["0439364264"]),
            ("439331188", ["0439331188"]),
            ("9780515202366", ["9780515202366"]),
            ("9780547199566", ["9780547199566"]),
        ],
    )
    def test_legacy_bib_data_validate_isbns(self, test_bib_data, arg, output):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "944",
                "fieldTag": "y",
                "subfields": [{"tag": "a", "content": arg}],
            }
        ]
        legacy_bib = LegacyBibData(
            bib_id=test_bib_data["id"],
            set_title=test_bib_data["title"],
            var_fields=test_bib_data["varFields"],
            language=test_bib_data["lang"],
        )
        assert legacy_bib.isbns == output

    @pytest.mark.parametrize(
        "arg,output",
        [
            ("9780789308849 9781234567890", ["9781234567890"]),
            ("978-0-78-930884-9 asdfgh", ["asdfgh"]),
            ("978-0-78-930884-X 068816241X", ["978078930884X"]),
            ("0-7893-0884-3 97897897X9", ["97897897X9"]),
            ("068816241X  0-7893-0884-Z ", ["078930884Z"]),
        ],
    )
    def test_legacy_bib_data_invalid_isbns(self, test_bib_data, arg, output):
        test_bib_data["varFields"] = [
            {
                "ind1": " ",
                "ind2": " ",
                "content": None,
                "marcTag": "944",
                "fieldTag": "y",
                "subfields": [{"tag": "a", "content": arg}],
            }
        ]
        with pytest.raises(ValueError) as exc:
            legacy_bib = LegacyBibData(
                bib_id=test_bib_data["id"],
                set_title=test_bib_data["title"],
                var_fields=test_bib_data["varFields"],
                language=test_bib_data["lang"],
            )
            legacy_bib.isbns
        assert (
            str(exc.value)
            == f"(19538471) Record contains 2 ISBN(s). 1/2 are invalid: {output}"
        )


class TestLegacyItemData:
    def test_legacy_item_data(self):
        legacy_item = LegacyItemData(
            item_id="i123456789",
            call_number="Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1",
            barcode="33333123456789",
        )
        assert (
            legacy_item.call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1-1"
        )
        assert (
            legacy_item.bib_call_number
            == "Teacher Set SOC A Book Club Set NYC History - This Is New York 1"
        )

    @pytest.mark.parametrize(
        "arg,result",
        [
            ("Math B Assorted 1-10", "Math B Assorted 1"),
            ("ELA D Genre - Horror 1-1", "ELA D Genre - Horror 1"),
            (
                "Language Arts ENG YA Book Club 185-5",
                "Language Arts ENG YA Book Club 185",
            ),
            (
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1-1",
                "SOC C Enhanced Book Club Set Narrative of the Life of Frederick Douglass 1",
            ),
            ("Arts A BIOG - Musicians (Jazz) 1-2", "Arts A BIOG - Musicians (Jazz) 1"),
            ("ELA D Horror Large Print 1-1", "ELA D Horror Large Print 1"),
            (
                "Language Arts ENG MG Book Club Graphic Novel 29-1",
                "Language Arts ENG MG Book Club Graphic Novel 29",
            ),
        ],
    )
    def test_legacy_item_data_call_number_patterns(self, arg, result):
        legacy_item = LegacyItemData(
            item_id="i123456789",
            call_number=f"Teacher Set {arg}",
            barcode="33333123456789",
        )
        assert legacy_item.call_number == f"Teacher Set {arg}"
        assert legacy_item.bib_call_number == f"Teacher Set {result}"


class TestLegacyTeacherSet:
    def test_legacy_set(self, legacy_set_test_data, caplog, mock_worldcat_response):
        legacy_set_data = LegacyTeacherSetData(**legacy_set_test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.parts[0].author == "Bar, Foo"
        assert legacy_set.parts[0].author_dates == "1980-"
        assert legacy_set.parts[0].description == "Fake description of book."
        assert legacy_set.parts[0].pub_date == "2000"
        assert len(legacy_set.parts[0].subjects) == 2
        assert (
            legacy_set.contents_note
            == 'Set consists of 2 copies of "Fake book 1", 2 copies of "Fake book 2".'
        )
        assert len(legacy_set.var_field_data) == 16
        assert legacy_set.legacy_barcodes == {
            "33333987654321": "Teacher Set SOC A Foo Bar Book Club 1-1",
            "33333123456789": "Teacher Set SOC A Foo Bar Book Club 1-2",
        }
        assert legacy_set.local_genre_term == ["Comics & Graphic Novels"]
        assert legacy_set.local_topic_term == ["New York City"]

    def test_legacy_set_single_copy(
        self, legacy_set_test_data, caplog, mock_worldcat_response
    ):
        legacy_set_test_data["set_parts"][0]["copies"] = 1
        legacy_set_test_data["set_parts"][1]["copies"] = 1
        legacy_set_data = LegacyTeacherSetData(**legacy_set_test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert (
            legacy_set.contents_note
            == 'Set consists of 1 copy of "Fake book 1", 1 copy of "Fake book 2".'
        )
        assert legacy_set.legacy_barcodes == {
            "33333987654321": "Teacher Set SOC A Foo Bar Book Club 1-1",
            "33333123456789": "Teacher Set SOC A Foo Bar Book Club 1-2",
        }

    @pytest.mark.parametrize(
        "subject,output",
        [
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Adventure stories")],
                },
                ["Adventure"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [
                        ("a", "Puerto Ricans"),
                        ("z", "New York (State)"),
                        ("z", "New York"),
                        ("v", "Biography."),
                    ],
                },
                ["Biography"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Fantasy fiction")],
                },
                ["Fantasy", "Fiction"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Literature and folklore")],
                },
                ["Folklore"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Manga (Comic books)")],
                },
                ["Comics & Graphic Novels", "Manga"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Autobiography")],
                },
                ["Memoir"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Cozy mysteries")],
                },
                ["Mystery"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Detective and mystery stories, Spanish")],
                },
                ["Mystery"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Russian American poetry")],
                },
                ["Poetry"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Romance fiction, English")],
                },
                ["Fiction", "Romance"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "1",
                    "tag": "650",
                    "subfields": [("a", "Family life"), ("v", "Fiction")],
                },
                ["Fiction"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "1",
                    "tag": "650",
                    "subfields": [("a", "Women"), ("v", "Biography")],
                },
                ["Biography"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Comics (Graphic works)."), ("2", "lcgft")],
                },
                ["Comics & Graphic Novels"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [
                        ("a", "Friendship"),
                        ("v", "Comic books, strips, etc."),
                    ],
                },
                ["Comics & Graphic Novels"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Coming-of-age comics"), ("2", "lcgft")],
                },
                ["Comics & Graphic Novels", "Coming of Age"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Memoirs"), ("2", "lcgft")],
                },
                ["Memoir"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [
                        ("a", "Detective and mystery fiction"),
                        ("2", "lcgft"),
                    ],
                },
                ["Fiction", "Mystery"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Love poetry"), ("2", "lcgft")],
                },
                ["Poetry"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Romance fiction"), ("2", "lcgft")],
                },
                ["Fiction", "Romance"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "7",
                    "tag": "655",
                    "subfields": [("a", "Nonfiction films"), ("2", "lcgft")],
                },
                ["Nonfiction"],
            ),
        ],
    )
    def test_legacy_set_local_genre_from_subjects(
        self, legacy_set_test_data, caplog, mock_worldcat_response, subject, output
    ):
        response = copy.deepcopy(mock_worldcat_response)
        response[0]["subjects"] = [subject]
        legacy_set_data = LegacyTeacherSetData(**legacy_set_test_data)
        legacy_set = LegacyTeacherSet(set_data=legacy_set_data, worldcat_parts=response)
        assert sorted([i.value for i in legacy_set.local_genre_term]) == sorted(output)

    @pytest.mark.parametrize(
        "title,output",
        [
            ("Schneider Family Book Award with Playaway Audiobook.", ["Award Winners"]),
            ("Animals - Easy Readers Nonfiction.", ["Nonfiction"]),
            ("Great Graphic Novels for Teens (Set V).", ["Comics & Graphic Novels"]),
            ("Caldecott Award Winners en espanol.", ["Award Winners"]),
        ],
    )
    def test_legacy_set_local_genre_from_title(
        self, legacy_set_test_data, caplog, mock_worldcat_response, title, output
    ):
        test_data = copy.deepcopy(legacy_set_test_data)
        test_data["set_title"] = title
        mock_worldcat_response[0]["subjects"] = []
        legacy_set_data = LegacyTeacherSetData(**test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.set_title == title
        assert sorted([i.value for i in legacy_set.local_genre_term]) == sorted(output)

    @pytest.mark.parametrize(
        "call_number,output",
        [
            ("Teacher Set ELA D Graphic Novels 3", ["Comics & Graphic Novels"]),
            ("Teacher Set SCI D Manga Guide 1", ["Manga"]),
            ("Teacher Set ELA B Poetry 3", ["Poetry"]),
            ("Teacher Set FRLA A Award Caldecott 2", ["Award Winners"]),
        ],
    )
    def test_legacy_set_local_genre_from_call_number(
        self, legacy_set_test_data, caplog, mock_worldcat_response, call_number, output
    ):
        test_data = copy.deepcopy(legacy_set_test_data)
        test_data["call_number"] = call_number
        mock_worldcat_response[0]["subjects"] = []
        legacy_set_data = LegacyTeacherSetData(**test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.call_number == call_number
        assert sorted([i.value for i in legacy_set.local_genre_term]) == sorted(output)

    @pytest.mark.parametrize(
        "subject,output",
        [
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "African Americans in motion pictures")],
                },
                ["African Americans"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "1",
                    "tag": "650",
                    "subfields": [("a", "African American athletes")],
                },
                ["African Americans", "Sports"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Asian Americans"), ("x", "Ethnic identity")],
                },
                ["Asian Americans"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "1",
                    "tag": "650",
                    "subfields": [("a", "Astronomy projects")],
                },
                ["Astronomy"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Autism spectrum disorders in children")],
                },
                ["Autism"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Behavior"), ("v", "Juvenile fiction")],
                },
                ["Behavior"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [
                        ("a", "Bullying"),
                        ("x", "Prevention"),
                        ("v", "Juvenile fiction"),
                    ],
                },
                ["Bullying"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Bullies"), ("v", "Juvenile fiction")],
                },
                ["Bullying"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Chinese Americans")],
                },
                ["Chinese Americans"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Civil rights movements")],
                },
                ["Civil Rights"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Community arts projects")],
                },
                ["Community"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Number concept")],
                },
                ["Concepts"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Concepts"), ("v", "Juvenile literature.")],
                },
                ["Concepts"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Cooking (Vegetables)")],
                },
                ["Cooking"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Courage in children")],
                },
                ["Courage"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Cultural Property")],
                },
                ["Cultural Heritage"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Dance"), ("v", "Juvenile fiction")],
                },
                ["Dance"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Family reunions")],
                },
                ["Family"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Immigrants")],
                },
                ["Immigration"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "New York (N.Y.)")],
                },
                ["New York City"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Heirloom varieties (Plants)")],
                },
                ["Plants"],
            ),
            (
                {
                    "ind1": " ",
                    "ind2": "0",
                    "tag": "650",
                    "subfields": [("a", "Plants and history")],
                },
                ["Plants"],
            ),
        ],
    )
    def test_legacy_set_local_topic_from_subject(
        self, legacy_set_test_data, caplog, mock_worldcat_response, subject, output
    ):
        response = copy.deepcopy(mock_worldcat_response)
        response[0]["subjects"] = [subject]
        legacy_set_data = LegacyTeacherSetData(**legacy_set_test_data)
        legacy_set = LegacyTeacherSet(set_data=legacy_set_data, worldcat_parts=response)
        assert sorted([i.value for i in legacy_set.local_topic_term]) == sorted(output)

    @pytest.mark.parametrize(
        "title,output",
        [
            ("Food and Nutrition - Seed to Food.", ["Health & Wellness"]),
            ("NYC Picture Books.", ["New York City"]),
            ("Communities", ["Community"]),
            ("Weather Picture Book Read Alouds with DVD.", ["Weather"]),
            ("Civil Rights Poetry", ["Civil Rights"]),
            ("Weather and Natural Disasters en espanol.", ["Weather"]),
            ("Exploring weather with DVD.", ["Weather"]),
            ("Ancient Civilization.", ["Ancient Civilization"]),
        ],
    )
    def test_legacy_set_local_topic_from_title(
        self, legacy_set_test_data, caplog, mock_worldcat_response, title, output
    ):
        test_data = copy.deepcopy(legacy_set_test_data)
        test_data["set_title"] = title
        mock_worldcat_response[0]["subjects"] = []
        legacy_set_data = LegacyTeacherSetData(**test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.set_title == title
        assert sorted([i.value for i in legacy_set.local_topic_term]) == sorted(output)

    @pytest.mark.parametrize(
        "call_number,output",
        [
            (
                "Teacher Set SOC B NYC History - Immigration 1",
                ["New York City", "Immigration"],
            ),
            ("Teacher Set ELA D NYC Fic 1", ["New York City"]),
            ("Teacher Set SCI A Reptiles 1", ["Animals"]),
            ("Teacher Set Math A Concepts 1", ["Concepts"]),
            ("Teacher Set SCI A Outer Space 1", ["Astronomy"]),
            ("Teacher Set SCI A Life Cycles - Plants and Seeds 1", ["Plants"]),
            (
                "Teacher Set SOC B Ancient Civilizations - Latin America 1",
                ["Ancient Civilization"],
            ),
        ],
    )
    def test_legacy_set_local_topic_from_call_number(
        self, legacy_set_test_data, caplog, mock_worldcat_response, call_number, output
    ):
        test_data = copy.deepcopy(legacy_set_test_data)
        test_data["call_number"] = call_number
        mock_worldcat_response[0]["subjects"] = []
        legacy_set_data = LegacyTeacherSetData(**test_data)
        legacy_set = LegacyTeacherSet(
            set_data=legacy_set_data, worldcat_parts=mock_worldcat_response
        )
        assert legacy_set.call_number == call_number
        assert sorted([i.value for i in legacy_set.local_topic_term]) == sorted(output)
