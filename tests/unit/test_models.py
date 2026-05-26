from mln_data_transform.models import (
    SubjectData,
    TeacherSetBib,
    TeacherSetBook,
    TeacherSetData,
    TeacherSetSpecialFormat,
)


class TestTeacherSetData:
    def test_teacher_set_data(self, set_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in set_test_data["parts"]]
        set_test_data["subjects"] = [
            SubjectData(
                tag=i["tag"], ind1=i["ind1"], ind2=i["ind2"], subfields=i["subfields"]
            )
            for i in set_test_data["subjects"]
        ]
        teacher_set = TeacherSetData(**set_test_data)
        assert teacher_set.leader == "00000nac  2200000 a 4500"
        assert teacher_set.control_number == "nn-mlnyc-0000001"
        assert teacher_set.begin_pub_date == "200101"
        assert teacher_set.end_pub_date == "200102"
        assert teacher_set.language == "eng"
        assert str(teacher_set.call_number) == "MLNYC ART-10 CLUB A FOO BAR 1-1"
        assert teacher_set.set_title == "Foo Bar Teacher Set"
        assert teacher_set.copy_data == "Copy 1 of 1"
        assert teacher_set.physical_description == "1 item"
        assert (
            teacher_set.contents_note
            == 'Set consists of 1 copy of "Foo Bar", 2 copies of "Test Title".'
        )
        assert teacher_set.grade_level == "Pre-K"
        assert teacher_set.study_program_info == "Arts & Music"
        assert teacher_set.bib_id == "b123456789"
        assert teacher_set.local_set_type == "Book Club"
        assert teacher_set.local_topic_term == ["New York City"]
        assert teacher_set.local_genre_term == ["Fiction"]
        assert teacher_set.items == []
        assert teacher_set.subjects == []
        assert teacher_set.library == "nypl"
        assert teacher_set.control_number_identifier == "BookOps"
        assert teacher_set.pub_place == "xxu"
        assert teacher_set.catalogers_initials == "mlnyc-bot"
        assert teacher_set.local_collection_code == "BL"
        assert teacher_set.oclc_exclusion_note == "OCLC Holdings Exclusion"
        assert teacher_set.location == "ed"
        assert teacher_set.material_type == "8"
        assert teacher_set.bib_code == "e"
        assert teacher_set.call_number.enumeration == "1-1"
        assert teacher_set.call_number.format == "CLUB"
        assert teacher_set.call_number.grade_level == "A"
        assert teacher_set.call_number.shelf_number == "10"
        assert teacher_set.call_number.subject_code == "ART"
        assert teacher_set.call_number.set_title == teacher_set.set_title.upper()
        assert teacher_set.call_number.enhanced is None

    def test_teacher_set_data_short_title(self, set_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in set_test_data["parts"]]
        set_test_data["set_title"] = "Storytelling"
        teacher_set = TeacherSetData(**set_test_data)
        assert str(teacher_set.call_number) == "MLNYC ART-10 CLUB A STORYTELLING 1-1"

    def test_teacher_set_data_enhanced(self, set_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in set_test_data["parts"]]
        set_test_data["parts"].append(
            TeacherSetSpecialFormat(
                title="Sock puppet", copies=1, description="A puppet."
            )
        )
        set_test_data["enhanced"] = "E"
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert str(teacher_set.call_number) == "MLNYC ART-10 CLUB E A FOO BAR 1-1"
        assert teacher_set.call_number.sub_f == "CLUB E"
        assert "=730  02$aSock puppet" in field_strings

    def test_teacher_set_bib(self, set_test_data, today_str):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in set_test_data["parts"]]
        set_test_data["subjects"] = [
            SubjectData(tag="650", ind1=" ", ind2="0", subfields=[("a", "Robots")])
        ]
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        field_strings = [str(i) for i in bib.fields]
        assert bib.leader == "00000nac  2200000 a 4500"
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  {today_str}i200101200102xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC ART-10$fCLUB$pA$cFOO BAR 1-1",
            "=245  00$aFoo Bar Teacher Set$cCopy 1 of 1",
            "=300  \\\\$a1 item",
            '=500  \\\\$aSet consists of 1 copy of "Foo Bar", 2 copies of "Test Title".',
            "=505  00$tFoo Bar /$rBaz --$tTest Title /$rFoo.",
            "=520  \\\\$3Foo Bar$aA book.",
            "=520  \\\\$3Test Title$aAnother book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aArts & Music",
            "=650  \\0$aRobots",
            "=690  \\7$aBook Club$2bookops",
            "=691  \\7$aNew York City$2bookops",
            "=695  \\7$aFiction$2bookops",
            "=700  12$aBaz$d2020-$tFoo Bar$f2025$x9781234567890",
            "=700  12$aFoo$tTest Title$f2025$x9780987654321",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=910  \\\\$aBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
        ]

    def test_teacher_set_bib_kit(self, set_test_data):
        set_test_data["parts"] = [TeacherSetBook(**i) for i in set_test_data["parts"]]
        set_test_data["record_type"] = "o"
        teacher_set = TeacherSetData(**set_test_data)
        set_bib = TeacherSetBib(data=teacher_set)
        bib = set_bib.to_bib()
        assert bib.leader == "00000noc  2200000 a 4500"
