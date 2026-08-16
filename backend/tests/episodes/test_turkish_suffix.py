from app.services.turkish_suffix import to_dative, to_genitive


def test_to_dative_and_to_genitive_match_the_documented_fixed_cast_examples() -> None:
    assert to_dative("Fındık") == "Fındık'a"
    assert to_dative("Minik") == "Minik'e"
    assert to_dative("Papatya") == "Papatya'ya"
    assert to_genitive("Boncuk") == "Boncuk'un"
    assert to_genitive("Zeytin") == "Zeytin'in"


def test_to_dative_buffers_third_person_possessive_place_names_with_n() -> None:
    assert to_dative("Büyük Meşe Ağacı") == "Büyük Meşe Ağacı'na"
    assert to_dative("Gökkuşağı Nehri") == "Gökkuşağı Nehri'ne"
    assert to_dative("Paylaşım Bahçesi") == "Paylaşım Bahçesi'ne"
    assert to_dative("Yıldız Tepesi") == "Yıldız Tepesi'ne"
