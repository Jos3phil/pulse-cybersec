"""T-E3-01 y T-E3-02. Necesitan la Clínica Inti encendida y sembrada con inti_full."""
import pytest

from tools.vigia_tools import listar_usuarios

pytestmark = pytest.mark.integration


def test_listar_usuarios_detects_seeded_inactive_accounts():  # T-E3-01
    out = listar_usuarios(threshold_days=90)
    assert out.total_accounts == 42
    assert out.inactive_accounts == 7


def test_listar_usuarios_boundary_is_strictly_greater():  # T-E3-02
    out = listar_usuarios(threshold_days=90)
    exactly_90 = [u for u in out.users if u.days_since_last_login == 90]
    assert exactly_90, "la siembra debe incluir una cuenta con acceso hace exactamente 90 días"
    assert out.inactive_accounts == len(
        [u for u in out.users if u.active and (u.days_since_last_login or 0) > 90]
    )
