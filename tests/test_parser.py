"""Parser tests using real lead-section templates from en.wikipedia.org."""

from lexphon.extraction.parser import extract_pronunciations

ISTANBUL = (
    "{{IPAc-en|lang|ˌ|ɪ|s|t|æ|n|ˈ|b|ʊ|l"
    "|audio=LL-Q1860 (eng)-Vealhurl-Istanbul.wav}} {{respell|IST|an|BUUL}}"
)
ZEUS = "{{IPAc-en|zj|u:|s}}"
YOSEMITE = "{{IPAc-en|j|oʊ|ˈ|s|ɛ|m|ɪ|t|i}} {{respell|yoh|SEM|ih|tee}}"
ALABAMA = "{{IPAc-en|,|æ|l|ə|'|b|æ|m|ə}} {{respell|AL|ə|BAM|ə}}"
EARTH = "'''Earth''' is the third planet from the [[Sun]] and the only known " \
        "astronomical object to [[Planetary habitability|harbor life]]."


def test_istanbul_records_both_native_forms():
    extracted = extract_pronunciations(ISTANBUL)
    assert extracted.ipa == "ˌɪstænˈbʊl"
    assert extracted.respell == "IST-an-BUUL"


def test_zeus_is_ipa_only_with_x_sampa_codes():
    extracted = extract_pronunciations(ZEUS)
    assert extracted.ipa == "zjuːs"
    assert extracted.respell is None


def test_yosemite_records_both_native_forms():
    extracted = extract_pronunciations(YOSEMITE)
    assert extracted.ipa == "joʊˈsɛmɪti"
    assert extracted.respell == "yoh-SEM-ih-tee"


def test_alabama_x_sampa_stress_marks_are_normalized():
    extracted = extract_pronunciations(ALABAMA)
    assert extracted.ipa == "ˌæləˈbæmə"
    assert extracted.respell == "AL-ə-BAM-ə"


def test_earth_without_template_is_skipped():
    extracted = extract_pronunciations(EARTH)
    assert extracted.ipa is None
    assert extracted.respell is None