import argparse

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


def test_load_requirements_accepts_empty_inline_value():
    args = argparse.Namespace(requirements="", requirements_file=None)
    assert app_builder.load_requirements(args) == ""


def test_generate_with_whitespace_inline_requirements_uses_fallback_feature(capsys):
    args = argparse.Namespace(
        command="generate",
        name="Test App",
        requirements="   \n\t",
        requirements_file=None,
        out="./output",
        stdout=True,
    )
    exit_code = app_builder.generate(args)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Core Workflow" in captured.out
