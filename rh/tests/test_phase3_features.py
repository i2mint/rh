"""Tests for Phase 3 features: presets, mobile CSS, arrays, conditional fields, and constraints."""

import pytest
from rh import MeshBuilder


def test_preset_values_in_html():
    """Test that preset values generate buttons in HTML."""
    mb = MeshBuilder(
        mesh_spec={"c": ["a", "b"]},
        functions_spec={"c": "return a + b;"},
        initial_values={"a": 1, "b": 2},
    )

    presets = {
        "Example 1": {"a": 5, "b": 10},
        "Example 2": {"a": 20, "b": 30},
    }

    app_file = mb.build_app(
        title="Preset Test",
        app_name="preset_test",
        presets=presets,
    )

    html = app_file.read_text()

    # Check that preset buttons are in the HTML
    assert "Example 1" in html
    assert "Example 2" in html
    assert "Presets:" in html
    assert 'onclick="if(window.renderForm) renderForm(' in html


def test_mobile_responsive_css():
    """Test that mobile-responsive CSS is included."""
    mb = MeshBuilder(
        mesh_spec={"c": ["a", "b"]},
        functions_spec={"c": "return a + b;"},
        initial_values={"a": 1, "b": 2},
    )

    # Test with embed_react=True
    app_file = mb.build_app(
        title="Mobile Test",
        app_name="mobile_test",
        embed_react=True,
    )

    html = app_file.read_text()

    # Check for mobile-responsive CSS
    assert "@media (max-width: 768px)" in html
    assert "@media (max-width: 480px)" in html
    assert "@media (hover: none) and (pointer: coarse)" in html
    assert "min-height: 44px" in html or "min-height: 48px" in html

    # Test with embed_react=False
    app_file2 = mb.build_app(
        title="Mobile Test 2",
        app_name="mobile_test2",
        embed_react=False,
    )

    html2 = app_file2.read_text()

    # Check for mobile-responsive CSS in CDN mode too
    assert "@media (max-width: 768px)" in html2
    assert "@media (max-width: 480px)" in html2


def test_array_schema_generation():
    """Test that arrays generate proper JSON Schema."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={
            "numbers": [1, 2, 3],
            "strings": ["a", "b", "c"],
            "empty_array": [],
        },
    )

    config = mb.generate_config()
    schema = config["schema"]

    # Check that arrays have proper schema
    assert schema["properties"]["numbers"]["type"] == "array"
    assert schema["properties"]["numbers"]["items"]["type"] == "integer"

    assert schema["properties"]["strings"]["type"] == "array"
    assert schema["properties"]["strings"]["items"]["type"] == "string"

    assert schema["properties"]["empty_array"]["type"] == "array"
    assert schema["properties"]["empty_array"]["items"]["type"] == "number"


def test_array_ui_conventions():
    """Test that array naming conventions work."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={
            "list_items": [1, 2, 3],
            "array_values": [4, 5, 6],
            "tags_keywords": ["tag1", "tag2"],
        },
    )

    config = mb.generate_config()
    ui_schema = config["uiSchema"]

    # Check that list_ and array_ prefixes add options
    assert "ui:options" in ui_schema.get("list_items", {})
    assert ui_schema["list_items"]["ui:options"]["addable"] == True
    assert ui_schema["list_items"]["ui:options"]["removable"] == True

    assert "ui:options" in ui_schema.get("array_values", {})

    # Check tags_ prefix
    assert "ui:options" in ui_schema.get("tags_keywords", {})


def test_conditional_fields_config():
    """Test that conditional fields are added to config."""
    mb = MeshBuilder(
        mesh_spec={"c": ["a", "b"]},
        functions_spec={"c": "return a + b;"},
        initial_values={"a": 1, "b": 2, "advanced": False},
        conditional_fields={
            "c": {
                "condition_field": "advanced",
                "condition_value": True,
                "condition_operator": "==",
            }
        },
    )

    config = mb.generate_config()

    # Check that conditional fields are in the config
    assert "conditional_fields" in config
    assert "c" in config["conditional_fields"]
    assert config["conditional_fields"]["c"]["condition_field"] == "advanced"


def test_conditional_fields_in_html():
    """Test that conditional fields JavaScript is generated."""
    mb = MeshBuilder(
        mesh_spec={"c": ["a", "b"]},
        functions_spec={"c": "return a + b;"},
        initial_values={"a": 1, "b": 2, "show_advanced": False},
        conditional_fields={
            "c": {
                "condition_field": "show_advanced",
                "condition_value": True,
                "condition_operator": "==",
            }
        },
    )

    app_file = mb.build_app(
        title="Conditional Test",
        app_name="conditional_test",
    )

    html = app_file.read_text()

    # Check that conditional fields JavaScript is present
    assert "applyConditionalVisibility" in html
    assert "conditionalFields" in html
    assert "show_advanced" in html


def test_constraint_descriptions():
    """Test that constraint descriptions are automatically generated."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={"slider": 50},
        field_overrides={
            "slider": {
                "minimum": 0,
                "maximum": 100,
            },
            "age": {
                "type": "integer",
                "minimum": 18,
            },
            "name": {
                "type": "string",
                "minLength": 3,
                "maxLength": 50,
            },
        },
    )

    config = mb.generate_config()
    schema = config["schema"]

    # Check that descriptions are added for constraints
    assert "description" in schema["properties"]["slider"]
    assert "between 0 and 100" in schema["properties"]["slider"]["description"]

    assert "description" in schema["properties"]["age"]
    assert "Minimum value: 18" in schema["properties"]["age"]["description"]

    assert "description" in schema["properties"]["name"]
    assert "Minimum length: 3" in schema["properties"]["name"]["description"]
    assert "Maximum length: 50" in schema["properties"]["name"]["description"]


def test_constraint_descriptions_dont_override():
    """Test that existing descriptions are not overridden."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={"slider": 50},
        field_overrides={
            "slider": {
                "minimum": 0,
                "maximum": 100,
                "description": "Custom description",
            }
        },
    )

    config = mb.generate_config()
    schema = config["schema"]

    # Check that custom description is preserved
    assert schema["properties"]["slider"]["description"] == "Custom description"


def test_enum_constraint_description():
    """Test that enum constraints generate descriptions."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={},
        field_overrides={
            "color": {
                "type": "string",
                "enum": ["red", "green", "blue"],
            }
        },
    )

    config = mb.generate_config()
    schema = config["schema"]

    # Check that enum description is generated
    assert "description" in schema["properties"]["color"]
    assert "Allowed values:" in schema["properties"]["color"]["description"]
    assert "red" in schema["properties"]["color"]["description"]
    assert "green" in schema["properties"]["color"]["description"]
    assert "blue" in schema["properties"]["color"]["description"]


def test_pattern_constraint_description():
    """Test that pattern constraints generate descriptions."""
    mb = MeshBuilder(
        mesh_spec={},
        functions_spec={},
        initial_values={},
        field_overrides={
            "email": {
                "type": "string",
                "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
            }
        },
    )

    config = mb.generate_config()
    schema = config["schema"]

    # Check that pattern description is generated
    assert "description" in schema["properties"]["email"]
    assert "Must match pattern:" in schema["properties"]["email"]["description"]
