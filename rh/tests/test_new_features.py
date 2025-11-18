"""Tests for new features: validation, utils, and extended widgets."""

import pytest
import tempfile
import json
from pathlib import Path
from rh import (
    MeshBuilder,
    validate_mesh,
    visualize_mesh,
    export_config,
    import_config,
    analyze_mesh_complexity,
    get_execution_order,
)
from rh.validation import MeshValidator


class TestValidation:
    """Tests for mesh validation functionality."""

    def test_valid_mesh_passes_validation(self):
        mesh_spec = {"y": ["x"]}
        functions_spec = {"y": "return x * 2;"}
        initial_values = {"x": 5}

        is_valid = validate_mesh(mesh_spec, functions_spec, initial_values)
        assert is_valid

    def test_undefined_dependency_fails_validation(self):
        mesh_spec = {"y": ["undefined_var"]}
        functions_spec = {"y": "return undefined_var * 2;"}
        initial_values = {}

        is_valid = validate_mesh(mesh_spec, functions_spec, initial_values)
        assert not is_valid

    def test_missing_function_implementation(self):
        mesh_spec = {"y": ["x"]}
        functions_spec = {}  # No implementation
        initial_values = {"x": 5}

        validator = MeshValidator()
        is_valid, errors = validator.validate_mesh_spec(
            mesh_spec, functions_spec, initial_values
        )

        assert not is_valid
        assert len(errors) > 0
        assert "no implementation" in errors[0]

    def test_circular_dependency_detection(self):
        mesh_spec = {"a": ["b"], "b": ["c"], "c": ["a"]}

        validator = MeshValidator()
        cycles = validator.detect_circular_dependencies(mesh_spec)

        assert len(cycles) > 0

    def test_function_syntax_validation(self):
        functions_spec = {
            "good": "return x * 2;",
            "bad_braces": "return x * 2;",
            "no_return": "x * 2;",  # Warning: no return
        }

        validator = MeshValidator()
        is_valid, errors = validator.validate_function_syntax(functions_spec)

        # Should have warnings but still be "valid" (warnings don't fail)
        assert any("no_return" in str(e) for e in errors)


class TestUtils:
    """Tests for utility functions."""

    def test_visualize_mesh(self):
        mesh_spec = {"y": ["x"], "z": ["y"]}
        initial_values = {"x": 5}

        viz = visualize_mesh(mesh_spec, initial_values)

        assert "INPUT VARIABLES" in viz
        assert "COMPUTED VARIABLES" in viz
        assert "x" in viz
        assert "y" in viz

    def test_analyze_mesh_complexity(self):
        mesh_spec = {"y": ["x"], "z": ["y"], "w": ["y", "z"]}

        metrics = analyze_mesh_complexity(mesh_spec)

        assert metrics["total_functions"] == 3
        assert metrics["max_dependencies"] == 2
        assert metrics["average_dependencies"] > 0

    def test_export_import_config(self):
        mesh_spec = {"y": ["x"]}
        functions_spec = {"y": "return x * 2;"}
        initial_values = {"x": 5}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            export_config(mesh_spec, functions_spec, initial_values, filepath)

            imported = import_config(filepath)

            assert imported["mesh_spec"] == mesh_spec
            assert imported["functions_spec"] == functions_spec
            assert imported["initial_values"] == initial_values
        finally:
            Path(filepath).unlink()

    def test_get_execution_order(self):
        mesh_spec = {"y": ["x"], "z": ["y"], "w": ["y"]}

        order = get_execution_order(mesh_spec)

        # Should have levels: first level has no deps, subsequent have resolved deps
        assert len(order) > 0


class TestExtendedWidgets:
    """Tests for new widget types."""

    def test_email_widget_convention(self):
        mesh_spec = {"email_output": ["email_address"]}
        functions_spec = {"email_output": "return email_address;"}
        initial_values = {"email_address": "test@example.com"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["email_address"]["ui:widget"] == "email"

    def test_url_widget_convention(self):
        mesh_spec = {"url_display": ["url_input"]}
        functions_spec = {"url_display": "return url_input;"}
        initial_values = {"url_input": "https://example.com"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["url_input"]["ui:widget"] == "url"

    def test_textarea_widget_convention(self):
        mesh_spec = {"textarea_output": ["textarea_description"]}
        functions_spec = {"textarea_output": "return textarea_description;"}
        initial_values = {"textarea_description": "Long text..."}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["textarea_description"]["ui:widget"] == "textarea"

    def test_tel_widget_convention(self):
        mesh_spec = {"tel_display": ["tel_phone"]}
        functions_spec = {"tel_display": "return tel_phone;"}
        initial_values = {"tel_phone": "555-1234"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["tel_phone"]["ui:widget"] == "tel"

    def test_time_widget_convention(self):
        mesh_spec = {"time_output": ["time_input"]}
        functions_spec = {"time_output": "return time_input;"}
        initial_values = {"time_input": "14:30"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["time_input"]["ui:widget"] == "time"

    def test_datetime_widget_convention(self):
        mesh_spec = {"datetime_output": ["datetime_input"]}
        functions_spec = {"datetime_output": "return datetime_input;"}
        initial_values = {"datetime_input": "2024-01-01T12:00"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["datetime_input"]["ui:widget"] == "datetime-local"

    def test_password_widget_convention(self):
        mesh_spec = {"password_hash": ["password_input"]}
        functions_spec = {"password_hash": "return password_input;"}
        initial_values = {"password_input": "secret"}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["password_input"]["ui:widget"] == "password"

    def test_number_widget_convention(self):
        mesh_spec = {"number_output": ["number_age"]}
        functions_spec = {"number_output": "return number_age;"}
        initial_values = {"number_age": 25}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["number_age"]["ui:widget"] == "updown"

    def test_checkbox_widget_convention(self):
        mesh_spec = {"checkbox_result": ["checkbox_agree"]}
        functions_spec = {"checkbox_result": "return checkbox_agree;"}
        initial_values = {"checkbox_agree": True}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["checkbox_agree"]["ui:widget"] == "checkbox"

    def test_range_widget_alias(self):
        """Test that range_ is an alias for slider_."""
        mesh_spec = {"range_output": ["range_value"]}
        functions_spec = {"range_output": "return range_value;"}
        initial_values = {"range_value": 50}

        builder = MeshBuilder(mesh_spec, functions_spec, initial_values)
        config = builder.generate_config()

        assert config["uiSchema"]["range_value"]["ui:widget"] == "range"


class TestExamples:
    """Test that example configurations are valid."""

    def test_temperature_converter_example(self):
        example_path = Path("/home/user/rh/examples/temperature_converter.json")
        if not example_path.exists():
            pytest.skip("Example file not found")

        config = import_config(str(example_path))

        is_valid = validate_mesh(
            config["mesh_spec"], config["functions_spec"], config["initial_values"]
        )

        assert is_valid

    def test_physics_calculator_example(self):
        example_path = Path("/home/user/rh/examples/physics_calculator.json")
        if not example_path.exists():
            pytest.skip("Example file not found")

        config = import_config(str(example_path))

        is_valid = validate_mesh(
            config["mesh_spec"], config["functions_spec"], config["initial_values"]
        )

        assert is_valid

    def test_loan_calculator_example(self):
        example_path = Path("/home/user/rh/examples/loan_calculator.json")
        if not example_path.exists():
            pytest.skip("Example file not found")

        config = import_config(str(example_path))

        is_valid = validate_mesh(
            config["mesh_spec"], config["functions_spec"], config["initial_values"]
        )

        assert is_valid
