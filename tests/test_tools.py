"""测试工具注册"""
import sys
sys.path.insert(0, "..")

from tools import registry


def test_registry_contains_tools():
    names = list(registry.tools.keys())
    assert "calculate" in names
    assert "get_weather" in names
    assert "get_hotlist" in names


def test_registry_generates_schemas():
    assert len(registry.schemas) == 3
    for schema in registry.schemas:
        assert schema["type"] == "function"
        assert "name" in schema["function"]
        assert "parameters" in schema["function"]


def test_calculator_invocation():
    assert "2" in registry.tools["calculate"]("1+1")
