from tool import app_builder


def test_extract_features_non_empty():
    req = "Must support login. Should include dashboard analytics. Nice to have dark mode."
    features = app_builder.extract_features(req)
    assert len(features) >= 3
    assert any(f.priority == "P0" for f in features)


def test_fallback_feature_when_requirements_too_short():
    features = app_builder.extract_features("hello")
    assert len(features) == 1
    assert features[0].name == "Core Workflow"
