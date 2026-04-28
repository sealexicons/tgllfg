
def test_ov_features_percolate():
    from tgllfg.pipeline import parse_text
    (_, f, _, _), = parse_text("Kinain ng aso ang isda.")[:1]
    assert f.feats["VOICE"] == "OV"
    assert f.feats["ASPECT"] == "PFV"
    assert f.feats["PRED"].startswith("EAT")
    assert "SUBJ" in f.feats and "OBJ" in f.feats
