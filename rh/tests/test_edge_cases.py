"""Tests for edge cases and error handling."""

import pytest
import tempfile
from rh import MeshBuilder


def test_empty_initial_values():
    """Test that empty initial values are handled correctly."""
    mesh_spec = {"y": ["x"], "z": ["y"]}
    functions_spec = {
        "y": "return x * 2;",
        "z": "return y + 10;",
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values={},  # Empty
    )

    config = builder.generate_config()
    assert config["initial_values"] == {}
    assert "schema" in config
    assert "x" in config["schema"]["properties"]


def test_circular_dependencies():
    """Test handling of circular dependencies in mesh."""
    mesh_spec = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],  # Circular
    }
    functions_spec = {
        "a": "return b + 1;",
        "b": "return c + 1;",
        "c": "return a + 1;",
    }
    initial_values = {"a": 1}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    # Should not raise an error during config generation
    config = builder.generate_config()
    assert "mesh" in config


def test_large_mesh():
    """Test handling of large mesh with many variables."""
    n = 50
    mesh_spec = {f"var_{i}": [f"var_{i-1}"] for i in range(1, n)}
    functions_spec = {f"var_{i}": f"return var_{i-1} + 1;" for i in range(1, n)}
    initial_values = {"var_0": 0}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    assert len(config["schema"]["properties"]) == n


def test_special_characters_in_variable_names():
    """Test variables with underscores and numbers."""
    mesh_spec = {
        "output_1": ["input_value"],
        "final_result_2": ["output_1"],
    }
    functions_spec = {
        "output_1": "return input_value * 2;",
        "final_result_2": "return output_1 + 100;",
    }
    initial_values = {"input_value": 50}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    assert "output_1" in config["schema"]["properties"]
    assert "final_result_2" in config["schema"]["properties"]


def test_numeric_initial_values():
    """Test different numeric types as initial values."""
    mesh_spec = {
        "output_int": ["input_int"],
        "output_float": ["input_float"],
        "output_negative": ["input_negative"],
    }
    functions_spec = {
        "output_int": "return input_int * 2;",
        "output_float": "return input_float * 1.5;",
        "output_negative": "return input_negative * -1;",
    }
    initial_values = {
        "input_int": 42,
        "input_float": 3.14159,
        "input_negative": -100,
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()

    # Check that types are inferred correctly
    # Integer values get type "integer", float values get "number"
    assert config["schema"]["properties"]["input_int"]["type"] == "integer"
    assert config["schema"]["properties"]["input_float"]["type"] == "number"
    assert config["schema"]["properties"]["input_negative"]["type"] == "integer"
    assert config["initial_values"]["input_int"] == 42
    assert config["initial_values"]["input_float"] == 3.14159


def test_string_initial_values():
    """Test string types as initial values."""
    mesh_spec = {"output": ["input"]}
    functions_spec = {"output": "return input.toUpperCase();"}
    initial_values = {"input": "hello world"}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    assert config["schema"]["properties"]["input"]["type"] == "string"
    assert config["initial_values"]["input"] == "hello world"


def test_boolean_initial_values():
    """Test boolean types as initial values."""
    mesh_spec = {"output": ["flag"]}
    functions_spec = {"output": "return flag ? 'yes' : 'no';"}
    initial_values = {"flag": True}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()
    assert config["schema"]["properties"]["flag"]["type"] == "boolean"
    assert config["initial_values"]["flag"] is True


def test_field_overrides_precedence():
    """Test that field_overrides take precedence over conventions."""
    mesh_spec = {"slider_value": ["input"]}
    functions_spec = {"slider_value": "return input * 2;"}
    initial_values = {"input": 50}

    # Override the slider convention
    field_overrides = {
        "slider_value": {
            "ui:widget": "text",  # Override slider to text
            "ui:readonly": True,
        }
    }

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
        field_overrides=field_overrides,
    )

    config = builder.generate_config()

    # Field override should win
    assert config["uiSchema"]["slider_value"]["ui:widget"] == "text"
    assert config["uiSchema"]["slider_value"]["ui:readonly"] is True


def test_multiple_dependencies():
    """Test variable with multiple dependencies."""
    mesh_spec = {
        "sum": ["a", "b", "c"],
        "product": ["a", "b"],
    }
    functions_spec = {
        "sum": "return a + b + c;",
        "product": "return a * b;",
    }
    initial_values = {"a": 2, "b": 3, "c": 5}

    builder = MeshBuilder(
        mesh_spec=mesh_spec,
        functions_spec=functions_spec,
        initial_values=initial_values,
    )

    config = builder.generate_config()

    # Check mesh structure
    assert config["mesh"]["sum"] == ["a", "b", "c"]
    assert config["mesh"]["product"] == ["a", "b"]

    # Check reverse mesh (camelCase)
    reverse = config["propagation_rules"]["reverseMesh"]
    assert "sum" in reverse["a"]
    assert "sum" in reverse["b"]
    assert "sum" in reverse["c"]
    assert "product" in reverse["a"]
    assert "product" in reverse["b"]


def test_app_builds_to_correct_location():
    """Test that app builds to the specified output directory."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 10}

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = f"{tmpdir}/my_custom_app"

        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=output_dir,
        )

        app_path = builder.build_app(title="Location Test")

        # Check that file was created in the right place
        assert str(app_path) == f"{output_dir}/index.html"
        assert app_path.exists()
        assert app_path.is_file()


def test_title_with_special_characters():
    """Test that titles with special characters are handled correctly."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        title = "Test <App> & \"Special\" 'Chars'"
        app_path = builder.build_app(title=title)

        with open(app_path) as f:
            content = f.read()

        # Title should be in the HTML
        assert title in content


def test_meta_information_in_html():
    """Test that meta information is rendered in generated HTML."""
    mesh_spec = {"y": ["x"]}
    functions_spec = {"y": "return x * 2;"}
    initial_values = {"x": 5}

    meta = {
        "description": "This is a test application",
        "features": ["Feature 1", "Feature 2", "Feature 3"],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        builder = MeshBuilder(
            mesh_spec=mesh_spec,
            functions_spec=functions_spec,
            initial_values=initial_values,
            output_dir=tmpdir,
        )

        app_path = builder.build_app(title="Meta Test", meta=meta)

        with open(app_path) as f:
            content = f.read()

        # Check that meta info is in HTML
        assert meta["description"] in content
        for feature in meta["features"]:
            assert feature in content
