"""Contrato: los ejemplos válidos pasan y los inválidos se rechazan (verde desde el día 1)."""
from contract.validator import validate_schema


def test_contract_findings_example_is_valid(load_example):
    assert validate_schema(load_example("findings_inti_full.json"), "findings.schema.json") == []


def test_contract_findings_rejects_free_text_in_facts(load_example):
    issues = validate_schema(load_example("findings_invalid_free_text.json"), "findings.schema.json")
    assert any("facts" in issue.path for issue in issues)


def test_contract_report_draft_example_is_valid(load_example):
    assert validate_schema(load_example("report_draft_valid.json"), "report_draft.schema.json") == []


def test_contract_report_draft_requires_citations(load_example):
    draft = load_example("report_draft_valid.json")
    draft["executive_summary"][0]["cites"] = []
    assert validate_schema(draft, "report_draft.schema.json") != []
