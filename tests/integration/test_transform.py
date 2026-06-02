# import pytest
# from dotenv import load_dotenv

# from mln_data_transform.legacy import LegacyBibData
# from mln_data_transform.models import TeacherSetBib
# from mln_data_transform.transform import LegacyTeacherSetBatch


# @pytest.fixture
# def test_legacy_bib(test_bib_data) -> LegacyBibData:
#     """Contains 7 item IDs, 1 ISBN, and notes there are 10 copies of the title."""
#     return LegacyBibData(
#         bib_id=test_bib_data["id"],
#         set_title=test_bib_data["title"],
#         fixed_fields=test_bib_data["fixedFields"],
#         var_fields=test_bib_data["varFields"],
#         language=test_bib_data["lang"]["code"],
#     )


# @pytest.fixture
# def test_bib(test_bib_multi_isbn) -> LegacyBibData:
#     """Contains 5 item IDs, 10 ISBNa, and notes there are 3 copies of each title."""
#     return LegacyBibData(
#         bib_id=test_bib_multi_isbn["id"],
#         set_title=test_bib_multi_isbn["title"],
#         fixed_fields=test_bib_multi_isbn["fixedFields"],
#         var_fields=test_bib_multi_isbn["varFields"],
#         language=test_bib_multi_isbn["lang"]["code"],
#     )


# class TestLegacyTeacherSetBatch:
#     load_dotenv()

#     @pytest.mark.livetest
#     def test_worldcat_data(self, today_str):
#         batch = LegacyTeacherSetBatch("20895133")
#         sets = batch.teacher_sets()
#         set_bib = TeacherSetBib(data=sets[0])
#         bib = set_bib.to_bib()
#         field_strings = [str(i) for i in bib.fields]
#         assert len(batch.worldcat_data.parts) == 8
#         assert [i.field_245.format_field() for i in sets] == [
#             "Ancient Civilizations. Copy 1 of 8",
#             "Ancient Civilizations. Copy 2 of 8",
#             "Ancient Civilizations. Copy 3 of 8",
#             "Ancient Civilizations. Copy 4 of 8",
#             "Ancient Civilizations. Copy 5 of 8",
#             "Ancient Civilizations. Copy 6 of 8",
#             "Ancient Civilizations. Copy 7 of 8",
#             "Ancient Civilizations. Copy 8 of 8",
#         ]
#         assert len(sets) == 8
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


# #     @pytest.mark.livetest
# #     def test_live_data(self, test_bib, today_str):
# #         batch = LegacyTeacherSetBatch(bib_data=test_bib)
# #         sets = batch.create_teacher_sets()
# #         set_bib = TeacherSetBib(data=sets[0])
# #         bib = set_bib.to_bib()
# #         field_strings = [str(i) for i in bib.fields]
# #         assert len(sets) == 5
# #         assert batch.worldcat_data.parts[0].title == "Little woodchucks"
# #         assert (
# #             batch.worldcat_data.parts[0].full_title
# #             == "Little woodchucks : Offerman woodshop's guide to tools and tomfoolery"
# #         )
# #         assert (
# #             batch.worldcat_data.parts[0].statement_of_responsibility
# #             == "Nick Offerman and Lee Buchanan"
# #         )
# #         assert batch.worldcat_data.parts[0].author == "Offerman, Nick"
# #         assert batch.worldcat_data.parts[0].author_dates == "1970-"
# #         assert (
# #             batch.worldcat_data.parts[0].description
# #             == '"From New York Times bestselling author, Emmy-winning actor, and charismatically carnivorous woodworker Nick Offerman, an illustrated woodworking guide with projects for the whole family"-- Provided by publisher.'
# #         )
# #         assert batch.worldcat_data.parts[0].pub_date == "2025"
# #         assert len(batch.worldcat_data.parts) == 10
# #         assert len(sets) == 1
# #         assert field_strings == [
# #             "=001  ",
# #             "=003  BookOps",
# #             f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
# #             "=091  \\\\$aMLNYC SOC-1$fCLUB$pA$cTHIS IS 1-1",
# #             "=245  00$aThis is New York : fake subtitle.$nCopy 1 of 10",
# #             "=300  \\\\$a1 item",
# #             '=500  \\\\$aSet consists of 1 copy of "This is New York".',
# #             "=520  \\\\$3This is New York$aFake description of book.",
# #             "=521  2\\$aPre-K",
# #             "=526  8\\$aSocial Studies",
# #             "=651  \\0$aNew York (N.Y.)",
# #             "=655  \\7$aFake genre.$2lcgft",
# #             "=690  \\7$aBook Club$2bookops",
# #             "=691  \\7$aNew York City$2bookops",
# #             "=695  \\7$aFiction$2bookops",
# #             "=700  12$aM. Sasek.$d1916-1980.$tThis is New York$f2025$x9780789308849",
# #             "=901  \\\\$amlnyc-bot$bCATBL",
# #             "=910  \\\\$aBL",
# #             "=909  \\\\$aOCLC Holdings Exclusion",
# #         ]

# #     def test_worldcat_data_mocked(self, test_legacy_bib, mock_responses):
# #         batch = LegacyTeacherSetBatch(bib_data=test_legacy_bib)
# #         assert batch.worldcat_data.parts[0].title == "This is New York"
# #         assert (
# #             batch.worldcat_data.parts[0].full_title
# #             == "This is New York : fake subtitle"
# #         )
# #         assert batch.worldcat_data.parts[0].statement_of_responsibility == "by M. Sasek"
# #         assert batch.worldcat_data.parts[0].author == "Sasek, M."
# #         assert batch.worldcat_data.parts[0].author_dates == "1916-1980."
# #         assert batch.worldcat_data.parts[0].description == "Fake description of book."
# #         assert batch.worldcat_data.parts[0].pub_date == "2003"
# #         assert len(batch.worldcat_data.parts) == 1

# #     def test_create_teacher_sets(self, test_legacy_bib, mock_responses, today_str):
# #         batch = LegacyTeacherSetBatch(bib_data=test_legacy_bib)
# #         sets = batch.create_teacher_sets()
# #         set_bib = TeacherSetBib(data=sets[0])
# #         bib = set_bib.to_bib()
# #         field_strings = [str(i) for i in bib.fields]
# #         assert len(sets) == 7
# #         assert field_strings == [
# #             "=001  ",
# #             "=003  BookOps",
# #             f"=008  {today_str}i20032003xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
# #             "=091  \\\\$aMLNYC SOC-1$fCLUB$pA$cTHIS IS 1-7",
# #             "=245  00$aThis is New York by M. Sasek.$nCopy 1 of 7",
# #             "=300  \\\\$a10 v.",
# #             '=500  \\\\$aSet consists of 10 copies of "This is New York".',
# #             "=520  \\\\$3This is New York$aFake description of book.",
# #             "=521  2\\$aPre-K",
# #             "=526  8\\$aSocial Studies",
# #             "=651  \\0$aNew York (N.Y.)",
# #             "=655  \\7$aFake genre.$2lcgft",
# #             "=690  \\7$aBook Club$2bookops",
# #             "=700  12$aSasek, M.$d1916-1980.$tThis is New York$f2003$x9780789308849",
# #             "=901  \\\\$amlnyc-bot$bCATBL",
# #             "=910  \\\\$aBL",
# #             "=909  \\\\$aOCLC Holdings Exclusion",
# #         ]


# # class TestLegacyTransformationComponents:
# #     def test_teacher_set(self, test_legacy_bib, test_item_data):
# #         # need to get item data from bib data (item ids)
# #         legacy_item = LegacyItemData(
# #             item_id=test_item_data["id"],
# #             call_number=test_item_data["callNumber"],
# #         )
# #         # need to get part data from bib data (isbns)
# #         for isbn in test_legacy_bib.isbns:
# #             part = TeacherSetBook(
# #                 full_title="Foo Bar : Baz",
# #                 title="Foo Bar",
# #                 author="Baz",
# #                 copies=test_legacy_bib.copy_info[0],
# #                 isbn=isbn,
# #                 description="A book.",
# #                 author_dates="2020-",
# #                 pub_date="2025",
# #             )
# #         new_set = TeacherSetData(
# #             bib_id=test_legacy_bib.bib_id,
# #             record_type=test_legacy_bib.record_type,
# #             physical_description=test_legacy_bib.physical_description,
# #             study_program_info=SubjectStudyProgram[legacy_item.subject],
# #             grade_level=GradeReadingLevel[legacy_item.grade_level],
# #             set_type=SetTypeFormat[legacy_item.set_type],
# #             enumeration=f"{legacy_item.set_copy_number}-{legacy_item.legacy_item_count}",
# #             set_title=test_legacy_bib.set_title,
# #             language=test_legacy_bib.language,
# #             shelf_number=legacy_item.shelf_number,
# #             parts=[part],
# #         )
# #         assert isinstance(new_set, TeacherSetData)
# #         assert new_set.leader == "00000nac  2200000 a 4500"
# #         assert new_set.control_number is None
# #         assert new_set.begin_pub_date == "uuuu"
# #         assert new_set.end_pub_date == "uuuu"
# #         assert new_set.language == "eng"
# #         assert str(new_set.call_number) == "MLNYC SOC-1 CLUB A THIS IS 1-7"
# #         assert new_set.set_title == "This is New York by M. Sasek."
# #         assert new_set.copy_data == "Copy 1 of 7"
# #         assert new_set.physical_description == "10 v."
# #         assert new_set.contents_note == 'Set consists of 10 copies of "Foo Bar".'
# #         assert new_set.grade_level == "Pre-K"
# #         assert new_set.study_program_info == "Social Studies"
# #         assert new_set.bib_id == "19538471"
# #         assert new_set.set_type == "Book Club"
# #         assert new_set.local_topic_term is None
# #         assert new_set.local_genre_term is None
# #         assert new_set.subjects is None
# #         assert new_set.library == "nypl"
# #         assert new_set.control_number_identifier == "BookOps"
# #         assert new_set.pub_place == "xxu"
# #         assert new_set.catalogers_initials == "mlnyc-bot"
# #         assert new_set.local_collection_code == "BL"
# #         assert new_set.oclc_exclusion_note == "OCLC Holdings Exclusion"
# #         assert new_set.location == "ed"
# #         assert new_set.material_type == "8"
# #         assert new_set.bib_code == "e"
# #         assert new_set.call_number.enumeration == "1-7"
# #         assert new_set.call_number.format == "CLUB"
# #         assert new_set.call_number.grade_level == "A"
# #         assert new_set.call_number.shelf_number == "1"
# #         assert new_set.call_number.subject_code == "SOC"
# #         assert new_set.call_number.set_title == new_set.set_title.upper()
# #         assert new_set.call_number.enhanced is None
