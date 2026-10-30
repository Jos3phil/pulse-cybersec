"""T-E6-01 (rojo hasta implementar tools/privacy_filter.py)."""
from tools.privacy_filter import filter_tool_output
from tools.vigia_tools import ListUsersOutput


def test_privacy_filter_drops_undeclared_name_field():  # T-E6-01
    raw = {
        "total_accounts": 42,
        "inactive_accounts": 7,
        "threshold_days": 90,
        "users": [],
        "nombre": "Juan Pérez",
    }
    result = filter_tool_output(raw, ListUsersOutput)
    assert "nombre" not in result.data
    assert result.dropped_fields == ["nombre"]
    assert result.data["inactive_accounts"] == 7


def test_privacy_filter_drops_free_text_inside_lists():
    raw = {
        "total_accounts": 1,
        "inactive_accounts": 0,
        "threshold_days": 90,
        "users": [{"subject": "Dra. Quispe", "active": True, "is_admin": False, "days_since_last_login": 3}],
    }
    result = filter_tool_output(raw, ListUsersOutput)
    assert "Quispe" not in str(result.data)
