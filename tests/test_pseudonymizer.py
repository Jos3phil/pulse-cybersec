"""T-E2-01 y T-E2-02 (rojo hasta implementar tools/pseudonymizer.py)."""
import re

from tools.pseudonymizer import pseudonymize


def test_pseudonymizer_is_stable_and_hides_username():  # T-E2-01
    a = pseudonymize("jperez", salt="sal-de-prueba")
    b = pseudonymize("jperez", salt="sal-de-prueba")
    assert a == b
    assert re.fullmatch(r"u_[0-9a-f]{6}", a)
    assert "jperez" not in a


def test_pseudonymizer_changes_with_salt():  # T-E2-02
    assert pseudonymize("jperez", salt="sal-1") != pseudonymize("jperez", salt="sal-2")
