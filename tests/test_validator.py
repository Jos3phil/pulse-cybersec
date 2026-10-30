"""T-E9-01 y T-E9-02 (rojo hasta implementar validate_draft_against_findings)."""
from contract.validator import validate_draft_against_findings


def test_validator_accepts_supported_draft(load_example):
    findings = load_example("findings_inti_full.json")
    draft = load_example("report_draft_valid.json")
    # Este borrador usa una norma aún no verificada en controls.yaml;
    # cuando se verifique, debe pasar sin errores.
    issues = validate_draft_against_findings(draft, findings)
    assert all("norma" in i.message for i in issues)


def test_validator_rejects_unknown_citation(load_example):  # T-E9-01
    issues = validate_draft_against_findings(
        load_example("report_draft_bad_cite.json"), load_example("findings_inti_full.json")
    )
    assert any("F-ACC-999" in i.message for i in issues)


def test_validator_rejects_unsupported_number(load_example):  # T-E9-02
    issues = validate_draft_against_findings(
        load_example("report_draft_bad_number.json"), load_example("findings_inti_full.json")
    )
    assert any("9" in i.message for i in issues)
