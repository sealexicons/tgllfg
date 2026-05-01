
def test_ov_features_percolate():
    from tgllfg.pipeline import parse_text
    (_, f, _, _), = parse_text("Kinain ng aso ang isda.")[:1]
    assert f.feats["VOICE"] == "OV"
    assert f.feats["ASPECT"] == "PFV"
    assert f.feats["PRED"].startswith("EAT")
    # OBJ-AGENT after the Phase 5b OBJ-θ-in-grammar alignment.
    assert "SUBJ" in f.feats and "OBJ-AGENT" in f.feats
