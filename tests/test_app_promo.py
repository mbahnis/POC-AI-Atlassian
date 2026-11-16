import pytest

from app.promo import CodePromoRefuse, appliquer_code


def test_code_valide_applique_la_reduction():
    assert appliquer_code(200.0, "BIENVENUE10")["total"] == 180.0


def test_code_insensible_a_la_casse():
    assert appliquer_code(200.0, " bienvenue10 ")["reduction"] == 20.0


def test_code_inconnu_refuse():
    with pytest.raises(CodePromoRefuse, match="Code promo inconnu"):
        appliquer_code(200.0, "FAUX")


def test_reduction_plafonnee_a_50_pourcent():
    assert appliquer_code(200.0, "MEGA70")["total"] == 100.0
