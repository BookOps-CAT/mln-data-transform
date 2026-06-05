import pytest
from dotenv import load_dotenv

from mln_data_transform.build import build_item_mapping, create_sets_from_data


class TestLegacyTeacherSetBatch:
    load_dotenv()

    def test_create_teacher_sets(self, mock_responses, today_str):
        bibs = create_sets_from_data(
            bib_id="19538471", item_mapping={"33333402207449": "358"}
        )
        set_bibs = [i.to_bib() for i in bibs]
        field_strings = [str(i) for i in set_bibs[0].fields]
        assert len(bibs[0].data.parts) == 1
        assert sorted([i.field_245.format_field() for i in bibs]) == sorted(
            ["This is New York by M. Sasek. Copy 1 of 1"]
        )
        assert len(bibs) == 1
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c358",
            "=245  00$aThis is New York by M. Sasek.$nCopy 1 of 1",
            "=300  \\\\$a10 v.",
            '=500  \\\\$aSet consists of 10 copies of "This is New York".',
            "=520  \\\\$3This is New York$aFake description of book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=651  \\0$aNew York (N.Y.)",
            "=655  \\7$aFake genre.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9780789308849",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
        ]

    @pytest.mark.livetest
    def test_worldcat_data_this_is_ny(self, today_str, caplog):
        item_mapping = build_item_mapping("data/260605_batch_01.csv")
        bibs = create_sets_from_data(
            bib_id="19538471", item_mapping=item_mapping["19538471"]
        )
        set_bibs = [i.to_bib() for i in bibs]
        field_strings = [str(i) for i in set_bibs[0].fields]
        assert len(bibs[0].data.parts) == 1
        assert sorted([i.field_245.format_field() for i in bibs]) == sorted(
            [
                "This is New York by M. Sasek. Copy 1 of 7",
                "This is New York by M. Sasek. Copy 2 of 7",
                "This is New York by M. Sasek. Copy 3 of 7",
                "This is New York by M. Sasek. Copy 4 of 7",
                "This is New York by M. Sasek. Copy 5 of 7",
                "This is New York by M. Sasek. Copy 6 of 7",
                "This is New York by M. Sasek. Copy 7 of 7",
            ]
        )
        assert len(bibs) == 7
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$cINC-1356",
            "=245  00$aThis is New York by M. Sasek.$nCopy 1 of 7",
            "=300  \\\\$a10 v.",
            '=500  \\\\$aSet consists of 10 copies of "This is New York".',
            "=520  \\\\$3This is New York$aA pictorial tour of Manhattan Island presenting drawings of its neighborhoods, transportation and traffic, buildings, and the city's activities, from the local shoeshine stall to Wall Street.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=651  \\0$aNew York (N.Y.)$xDescription and travel$vJuvenile literature.",
            "=655  \\0$aPicture books for children.$5NZ-WeK",
            "=655  \\7$aLiterature.$2lcgft",
            "=655  \\7$aIllustrated works.$2lcgft",
            "=690  \\7$aBook Club$2bookops",
            "=700  12$aSasek, M.$d1916-1980$tThis is New York$f2003$x9780789308849",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
        ]
        assert (
            len(caplog.records) == 5
        )  # should be the number of volumes in set x 3 + 2

    @pytest.mark.livetest
    def test_worldcat_data_ancient_civ(self, today_str, caplog):
        item_mapping = build_item_mapping("data/260605_batch_01.csv")
        bibs = create_sets_from_data(
            bib_id="20895133", item_mapping=item_mapping["20895133"]
        )
        set_bibs = [i.to_bib() for i in bibs]
        field_strings = [str(i) for i in set_bibs[0].fields]
        assert len(bibs[0].data.parts) == 8
        assert sorted([i.field_245.format_field() for i in bibs]) == sorted(
            [
                "Ancient Civilizations. Copy 1 of 8",
                "Ancient Civilizations. Copy 2 of 8",
                "Ancient Civilizations. Copy 3 of 8",
                "Ancient Civilizations. Copy 4 of 8",
                "Ancient Civilizations. Copy 5 of 8",
                "Ancient Civilizations. Copy 6 of 8",
                "Ancient Civilizations. Copy 7 of 8",
                "Ancient Civilizations. Copy 8 of 8",
            ]
        )
        assert len(bibs) == 8
        assert field_strings == [
            "=001  ",
            "=003  BookOps",
            f"=008  {today_str}i20152015xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fTOPIC$pC$c1077",
            "=245  00$aAncient Civilizations.$nCopy 1 of 8",
            "=300  \\\\$a8 v.",
            '=500  \\\\$aSet consists of 1 copy of "Ancient Rome", 1 copy of "Ancient Mesopotamia", 1 copy of "Ancient Maya", 1 copy of "Ancient India", 1 copy of "Ancient Greece", 1 copy of "Ancient Egypt", 1 copy of "Ancient China", 1 copy of "Ancient Aztecs".',
            "=520  \\\\$3Ancient Rome$aIn Ancient Rome, readers discover the history and impressive accomplishments of the ancient Romans, including their military power and feats of engineering. Text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.",
            "=520  \\\\$3Ancient Mesopotamia$a\"In Ancient Mesopotamia, readers discover the history and impressive accomplishments of the ancient Mesopotamians, including their extraordinary cultural achievements and technological wonders. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=520  \\\\$3Ancient Maya$a\"In Ancient Maya, readers discover the history and impressive accomplishments of the Maya people, including their advanced mathematics and massive stone cities. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient India$a\"In Ancient India, readers discover the history and impressive accomplishments of the people of ancient India, including their enduring religions and rich literary traditions. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=520  \\\\$3Ancient Greece$aReaders will discover the history and accomplishments of the people of ancient Greece, including their cultural achievements and feats of construction.",
            "=520  \\\\$3Ancient Egypt$a\"In Ancient Egypt, readers discover the history and impressive accomplishments of the people of ancient Egypt, including their extraordinary cultural achievements and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient China$a\"In Ancient China, readers discover the history and impressive accomplishments of the people of ancient China, including their technological wonders and feats of construction. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's website.",
            "=520  \\\\$3Ancient Aztecs$a\"In Ancient Aztecs, readers discover the history and impressive accomplishments of the Aztec civilization, including their military power and feats of engineering. Engaging text provides details on the civilization's history, development, daily life, culture, art, technology, warfare, social organization, and more.\"--Publisher's web site.",
            "=521  2\\$a3-5",
            "=526  8\\$aSocial Studies",
            "=650  \\0$aMayas$vJuvenile literature.",
            "=650  \\0$aAztecs$vJuvenile literature.",
            "=651  \\0$aRome$xCivilization.",
            "=651  \\0$aRome$xHistory.",
            "=651  \\0$aRome$xSocial life and customs.",
            "=651  \\0$aIraq$xHistory$yTo 634$vJuvenile literature.",
            "=651  \\0$aIraq$xCivilization$yTo 634$vJuvenile literature.",
            "=651  \\0$aMexico$xCivilization$vJuvenile literature.",
            "=651  \\0$aCentral America$xCivilization$vJuvenile literature.",
            "=651  \\0$aIndia$xCivilization$yTo 1200$vJuvenile literature.",
            "=651  \\0$aGreece$xCivilization$yTo 146 B.C.$vJuvenile literature.",
            "=651  \\0$aEgypt$xCivilization$yTo 332 B.C.$vJuvenile literature.",
            "=651  \\0$aChina$xCivilization$yTo 221 B.C.$vJuvenile literature.",
            "=651  \\0$aChina$xCivilization$y221 B.C.-960 A.D.$vJuvenile literature.",
            "=651  \\0$aChina$xHistory$vJuvenile literature.",
            "=651  \\0$aGreece$xSocial life and customs$vJuvenile literature.",
            "=655  \\7$aLiterature.$2lcgft",
            "=690  \\7$aTopic$2bookops",
            "=700  12$aHamen, Susan E.$tAncient Rome$f2015$x9781624035425",
            "=700  12$aHead, Tom$tAncient Mesopotamia$f2015$x9781624035418",
            "=700  12$aEdwards, Sue Bradford$tAncient Maya$f2015$x9781624035401",
            "=700  12$aRowell, Rebecca$tAncient India$f2015$x9781624035395",
            "=700  12$aBailey, Diane$d1966-$tAncient Greece$f2015$x9781624035388",
            "=700  12$aAmstutz, Lisa J.$tAncient Egypt$f2015$x9781624035371",
            "=700  12$aAtkins, Marcie Flinchum$tAncient China$f2015$x9781624035364",
            "=700  12$aKenney, Karen Latchana$tAncient Aztecs$f2015$x9781624035357",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
        ]
        assert len(caplog.records) == 26

    def test_build_item_mapping(self, caplog):
        item_mapping = build_item_mapping("data/260605_batch_01.csv")
        assert item_mapping["19963240"] == {
            "33333837268594": "558",
            "33333837269519": "559",
        }


#     @pytest.mark.livetest
#     def test_live_data(self, test_bib, today_str):
#         batch = LegacyTeacherSetBatch(bib_data=test_bib)
#         sets = batch.create_teacher_sets()
#         set_bib = TeacherSetBib(data=sets[0])
#         bib = set_bib.to_bib()
#         field_strings = [str(i) for i in bib.fields]
#         assert len(sets) == 5
#         assert batch.worldcat_data.parts[0].title == "Little woodchucks"
#         assert (
#             batch.worldcat_data.parts[0].full_title
#             == "Little woodchucks : Offerman woodshop's guide to tools and tomfoolery"
#         )
#         assert (
#             batch.worldcat_data.parts[0].statement_of_responsibility
#             == "Nick Offerman and Lee Buchanan"
#         )
#         assert batch.worldcat_data.parts[0].author == "Offerman, Nick"
#         assert batch.worldcat_data.parts[0].author_dates == "1970-"
#         assert (
#             batch.worldcat_data.parts[0].description
#             == '"From New York Times bestselling author, Emmy-winning actor, and charismatically carnivorous woodworker Nick Offerman, an illustrated woodworking guide with projects for the whole family"-- Provided by publisher.'
#         )
#         assert batch.worldcat_data.parts[0].pub_date == "2025"
#         assert len(batch.worldcat_data.parts) == 10
#         assert len(sets) == 1
#         assert field_strings == [
#             "=001  ",
#             "=003  BookOps",
#             f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
#             "=091  \\\\$aMLNYC SOC-1$fCLUB$pA$cTHIS IS 1-1",
#             "=245  00$aThis is New York : fake subtitle.$nCopy 1 of 10",
#             "=300  \\\\$a1 item",
#             '=500  \\\\$aSet consists of 1 copy of "This is New York".',
#             "=520  \\\\$3This is New York$aFake description of book.",
#             "=521  2\\$aPre-K",
#             "=526  8\\$aSocial Studies",
#             "=651  \\0$aNew York (N.Y.)",
#             "=655  \\7$aFake genre.$2lcgft",
#             "=690  \\7$aBook Club$2bookops",
#             "=691  \\7$aNew York City$2bookops",
#             "=695  \\7$aFiction$2bookops",
#             "=700  12$aM. Sasek.$d1916-1980.$tThis is New York$f2025$x9780789308849",
#             "=901  \\\\$amlnyc-bot$bCATBL",
#             "=910  \\\\$aBL",
#             "=909  \\\\$aOCLC Holdings Exclusion",
#         ]
