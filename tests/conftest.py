import json
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "contract" / "examples"


@pytest.fixture
def load_example():
    def _load(name: str) -> dict:
        return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
    return _load
